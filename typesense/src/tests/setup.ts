module.exports = async function () {
  const shell = require("shelljs")
  const port = 1818
  const mockDataPath = "../../data/test_omp_data.json"
  shell.echo("making sure typesense docker image is installed")
  shell.exec("bash ./scripts/setup.sh")
  shell.exec(`bash ./scripts/start-server.sh ${port}`, {async:true})
  shell.exec(`bash ./scripts/index-docs.sh ${mockDataPath} ${port}`)

  let isServerReady = false
  while (!isServerReady) {
    const healthOutput = shell.exec(`curl http://localhost:${port}/health`)
    if (healthOutput.stdout === '{"ok":true}') {
      console.log("server ready for requests")
      isServerReady = true
    }
    await new Promise(r => setTimeout(r, 1000))
  }
  shell.exec("bash ./scripts/index-test-docs.sh")

  console.log("server ready for testing")
};