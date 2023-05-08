port=8108
#relative to src
datapath="../data/test_omp_data.json"


until [ $serverReady == true ];
do 
  echo "waiting for server..."
  sleep 2
  serverReady=$(bash ./scripts/check-server.sh "$port")
done
echo "server ready for requests"

bash index-docs.sh "$datapath" "$port"

curl -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
    "http://localhost:$port/collections"