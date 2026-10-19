# Shared SSM helpers, sourced by prod-deploy.fish and staging-deploy.fish.
# Expects $region to be set by the caller.

function run_ssm -a instance cmd
    set -l id (aws ssm send-command --region $region --instance-ids $instance \
        --document-name AWS-RunShellScript \
        --parameters (jq -cn --arg c $cmd '{commands: [$c]}') \
        --query Command.CommandId --output text); or return 1
    set -l st ""
    while true
        set st (aws ssm get-command-invocation --region $region --command-id $id \
            --instance-id $instance --query Status --output text 2>/dev/null)
        switch "$st"
            case Pending InProgress Delayed ''
                sleep 5
            case '*'
                break
        end
    end
    aws ssm get-command-invocation --region $region --command-id $id --instance-id $instance \
        --query '[StandardOutputContent,StandardErrorContent]' --output text | tail -n 15
    test "$st" = Success
end

function wait_ssm -a instance
    set -l ping ""
    for i in (seq 60)
        set ping (aws ssm describe-instance-information --region $region \
            --filters Key=InstanceIds,Values=$instance \
            --query 'InstanceInformationList[0].PingStatus' --output text)
        test "$ping" = Online; and return 0
        sleep 5
    end
    return 1
end