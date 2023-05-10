port=8108
#relative to src
datapath="../data/test_omp_data.json"


until [ $serverReady == true ];
do 
  echo "waiting for server..."
  sleep 2
  serverReady=$(bash $(dirname $0)/scripts/check-server.sh "$port")
done
echo "server ready for requests"

bash $(dirname $0)/scripts/index-docs.sh "$datapath" "$port"

curl -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
    "http://localhost:$port/collections"