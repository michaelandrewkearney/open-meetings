port=8101
datapath="./data/test_omp_data"

bash ./scripts/setup.sh 
bash ./scripts/start-server.sh 8108

serverReady=$(bash ./scripts/check-server.sh )

until [ $serverReady == true] 
do 
  echo "server still starting..."
  sleep 2
  serverReady=$(bash ./scripts/check-server.sh )
done

echo "server ready for requests"