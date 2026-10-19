#!/usr/bin/env fish
# Blue/green prod deploy.
# Usage: scripts/prod-deploy.fish <backend_tag> <frontend_tag>
# Upload the compose files to s3://fireaway-ryan-artifacts/deploy/ first.

set -g region us-east-1
set -l repo 856820204904.dkr.ecr.us-east-1.amazonaws.com
set -q DRAIN; or set DRAIN 420 # seconds to keep old colour up | (360 s result poll + margin)

function fail
    echo "x $argv" >&2
    exit 1
end

source (dirname (status filename))/lib/ssm.fish

function instance_id -a colour
    aws ec2 describe-instances --region $region \
        --filters Name=tag:Name,Values=fireaway-prod-$colour Name=instance-state-name,Values=pending,running,stopping,stopped \
        --query 'Reservations[0].Instances[0].InstanceId' --output text
end

function swap_to -a instance colour
    aws ec2 associate-address --region $region --allocation-id $eip_alloc \
        --instance-id $instance --allow-reassociation >/dev/null; or return 1
    aws ssm put-parameter --region $region --name /fireaway/prod/active_color \
        --value $colour --overwrite >/dev/null
end

# inputs
test (count $argv) -eq 2; or fail "usage: prod-deploy.fish <backend_tag> <frontend_tag>"
for pair in fireaway-ryan-backend:$argv[1] fireaway-ryan-frontend:$argv[2]
    set -l parts (string split : $pair)
    aws ecr describe-images --region $region --repository-name $parts[1] \
        --image-ids imageTag=$parts[2] >/dev/null 2>&1; or fail "image $pair not found in ECR (was this exact tree deployed to staging first?)"
end
set -l backend $repo/fireaway-ryan-backend:$argv[1]
set -l frontend $repo/fireaway-ryan-frontend:$argv[2]

#sync the deploy config from this checkout it has to match what is committed
set -l root (git rev-parse --show-toplevel); or fail "run from inside the repo"
set -l cfg docker-compose.yml docker-compose.prod.yml terraform/templates/Caddyfile.prod
git -C $root diff --quiet HEAD -- $cfg; or fail "uncommitted changes in $cfg"
for f in $cfg
    aws s3 cp $root/$f s3://fireaway-ryan-artifacts/deploy/(basename $f) --region $region >/dev/null
    or fail "upload of $f failed"
end

set -g eip_alloc (aws ec2 describe-addresses --region $region \
    --filters Name=tag:Name,Values=fireaway-prod-live \
    --query 'Addresses[0].AllocationId' --output text)

set -l live (aws ssm get-parameter --region $region --name /fireaway/prod/active_color \
    --query Parameter.Value --output text); or fail "cannot read active colour"
set -l idle green
test "$live" = green; and set idle blue
set -l live_id (instance_id $live)
set -l idle_id (instance_id $idle)
echo "live: $live ($live_id)  deploying to: $idle ($idle_id)"

# start idle
aws ec2 start-instances --region $region --instance-ids $idle_id >/dev/null
aws ec2 wait instance-running --region $region --instance-ids $idle_id

wait_ssm $idle_id; or fail "$idle never registered with ssm"

#deploy to idle
echo "deploying $argv[1] $argv[2] to $idle..."
if not run_ssm $idle_id "sudo /opt/fireaway/deploy.sh $backend $frontend"
    aws ec2 stop-instances --region $region --instance-ids $idle_id >/dev/null
    fail "deploy to $idle failed; $live is untouched and still running"
end

# swap
echo "switching prod EIP to $idle...."
swap_to $idle_id $idle; or fail "EIP swap failed; $live is still running"

set -l code ""
for i in (seq 24) # 2 min cover for caddy file cert on first swap
    set code (curl -s -o /dev/null -w '%{http_code}' --max-time 5 https://fireaway.site/health)
    test "$code" = 200; and break
    sleep 5
end
if test "$code" != 200
    echo "X fireaway.site not healthy on $idle (last status code: $code), rolling back to $live" >&2
    swap_to $live_id $live
    exit 1
end
echo "$idle is live and running"

# stop old 
echo "keeping $live up for $DRAIN s for current busy jobs. Roll back now:"
echo "  aws ec2 associate-address --region $region --allocation-id $eip_alloc --instance-id $live_id --allow-reassociation"
echo "  aws ssm put-parameter --region $region --name /fireaway/prod/active_color --value $live --overwrite"
sleep $DRAIN
aws ec2 stop-instances --region $region --instance-ids $live_id >/dev/null
echo "$live stopped"