CONTAINER_REGISTRY=$(cat package.json | jq .repository --raw-output)
IMAGE_NAME=$(cat package.json | jq .name --raw-output)
IMAGE_VERSION=$(cat package.json | jq .version --raw-output)
COMMIT_HASH=$(git rev-parse --short HEAD)

IMAGE_NAME="$CONTAINER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION"
FULL_IMAGE_NAME="$IMAGE_NAME-$COMMIT_HASH"

docker build -t $IMAGE_NAME -t $FULL_IMAGE_NAME .
docker push $IMAGE_NAME
docker push $FULL_IMAGE_NAME