# VITE_APPSYNC_REALTIME_ENDPOINT=$(aws ssm get-parameter --name "/${DEPLOYMENT_ID}/bff/appsync-realtime-endpoint" --query 'Parameter.Value' --output text --region $AWS_REGION)
# echo "AppSync Native Host: $VITE_APPSYNC_REALTIME_ENDPOINT"
# VITE_APPSYNC_HTTP_ENDPOINT=$(aws ssm get-parameter --name "/${DEPLOYMENT_ID}/bff/appsync-http-endpoint" --query 'Parameter.Value' --output text --region $AWS_REGION)
# echo "AppSync HTTP Endpoint: $VITE_APPSYNC_HTTP_ENDPOINT"

cd frontend
npm config set update-notifier false
yarn install --no-progress --frozen-lockfile
VITE_APPSYNC_REALTIME_ENDPOINT=$(aws ssm get-parameter --name "/${DEPLOYMENT_ID}/bff/appsync-realtime-endpoint" --query 'Parameter.Value' --output text --region $AWS_REGION) VITE_APPSYNC_HTTP_ENDPOINT=$(aws ssm get-parameter --name "/${DEPLOYMENT_ID}/bff/appsync-http-endpoint" --query 'Parameter.Value' --output text --region $AWS_REGION) yarn build:ci
cd ..
