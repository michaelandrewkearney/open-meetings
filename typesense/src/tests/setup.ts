module.exports = async function () {
  const shell = require("shelljs")
  const port = 1818
  shell.echo("making sure typesense docker image is installed")
  shell.exec("bash ./scripts/setup.sh")
  shell.exec(`bash ./scripts/run.sh ${port}`, {async:true})

  let isServerReady = false
  while (!isServerReady) {
    const healthOutput = shell.exec(`curl http://localhost:${port}/health`)
    if (healthOutput.stdout === '{"ok":true}') {
      console.log("server ready for requests")
      isServerReady = true
    }
    await new Promise(r => setTimeout(r, 1000))
  }
  shell.exec("bash ./scripts/add-test-docs.sh")

  console.log("server ready for testing")
};