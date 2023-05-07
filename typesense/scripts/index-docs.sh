datapath=$1
port=$2

until [ $serverReady == true ]
do 
  echo "waiting for server..."
  sleep 2
  serverReady=$(bash ./scripts/check-server.sh 8108)
done
echo "server ready for requests"

npx ts-node ./src/add_documents.ts "$datapath" "$port"