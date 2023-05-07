datapath=$1
port=$2

npx ts-node ./src/add_documents.ts "$datapath" "$port"