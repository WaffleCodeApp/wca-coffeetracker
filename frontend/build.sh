# must be relative to the current directory
npm config set update-notifier false
yarn install --no-progress --frozen-lockfile
yarn build:ci
