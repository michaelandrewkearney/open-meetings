module.exports = async function () {
  const shell = require("shelljs")

  console.log("tearing down server")
  shell.exec("bash ./scripts/teardown-test-server.sh")
};