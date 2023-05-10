module.exports = async function () {
  const shell = require("shelljs")
  const port = 1818
  const mockDataPath = "../data/test_omp_data.json"
  shell.echo("making sure typesense docker image is installed")
  shell.exec("bash ./scripts/setup.sh")
  shell.exec(`bash ./scripts/start-test-server.sh ${port}`, {async:true})

  let isServerReady = false

  while (!isServerReady) {
    console.log("checking if server is ready")
    const healthOutput = shell.exec(`curl -s http://localhost:${port}/health`)
    if (healthOutput.stdout === '{"ok":true}') {
      console.log("server ready for requests")
      isServerReady = true
    }
    await new Promise(r => setTimeout(r, 3000))
  }
  shell.exec(`bash ./scripts/index-docs.sh ${mockDataPath} ${port}`)

  console.log("server ready for testing")
};