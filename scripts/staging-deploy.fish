#!/usr/bin/env fish
# Staging deploy
# Usage: scripts/staging-deploy.fish <backend_tag> <frontend_tag>

set -g region us-east-1
set -l repo 856820204904.dkr.ecr.us-east-1.amazonaws.com

function fail
    echo "x $argv" >&2
    exit 1
end

source (dirname (status filename))/lib/ssm.fish

#inputs
test (count $argv) -eq 2; or fail "usage: staging-deploy.fish <backend_tag> <frontend_tag>"
for pair in fireaway-ryan-backend:$argv[1] fireaway-ryan-frontend:$argv[2]
    set -l parts (string split : $pair)
    aws ecr describe-images --region $region --repository-name $parts[1] \
        --image-ids imageTag=$parts[2] >/dev/null 2>&1; or fail "image $pair not found in ECR"
end
set -l backend $repo/fireaway-ryan-backend:$argv[1]
set -l frontend $repo/fireaway-ryan-frontend:$argv[2]

# sync the deploy config from this checkout has to match whats commited
set -l root (git rev-parse --show-toplevel); or fail "run from inside the repo"
set -l cfg docker-compose.yml docker-compose.staging.yml terraform/templates/Caddyfile.staging
git -C $root diff --quiet HEAD -- $cfg; or fail "uncommitted changes in $cfg"
for f in $cfg
    aws s3 cp $root/$f s3://fireaway-ryan-artifacts/deploy/(basename $f) --region $region >/dev/null
    or fail "upload of $f failed"
end

# start staging if its stopped
set -l id (aws ec2 describe-instances --region $region \
    --filters Name=tag:Name,Values=fireaway-staging Name=instance-state-name,Values=pending,running,stopping,stopped \
    --query 'Reservations[0].Instances[0].InstanceId' --output text)
test "$id" != None; or fail "staging instance not found"

aws ec2 start-instances --region $region --instance-ids $id >/dev/null
aws ec2 wait instance-running --region $region --instance-ids $id
wait_ssm $id; or fail "staging never registered with ssm"

# deploy
echo "deploying $argv[1] $argv[2] to staging ($id)..."
run_ssm $id "sudo /opt/fireaway/deploy.sh $backend $frontend"; or fail "deploy to staging failed"

# external health check through Caddy
set -l code ""
for i in (seq 24)
    set code (curl -s -o /dev/null -w '%{http_code}' --max-time 5 https://staging-fireaway.csml.co.za/health)
    test "$code" = 200; and break
    sleep 5
end
test "$code" = 200; or fail "staging not healthy (last status: $code)"
echo "staging is live"