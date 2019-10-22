ProActive Agent is a system daemon to automatically starts ProActive runtimes according to a weekly schedule

# Testing

You can test parsing all configuration files by simply running:

```bash
./run-tests.sh
```

A blackbox test is also available, first build the blackbox test from the agent-linux root.

```bash
PYTHONPATH=. python palinagent/daemon/tests/blackbox/build_jar.py
```

For running the blackbox test use:

```bash
PYTHONPATH=. python palinagent/daemon/tests/blackbox/testblackbox.py
```



# Changing schema


Schema is hardcoded in several part, including the tests.

First create your new schema on a separate folder, for instance:

```bash
cp -fr palinagent/daemon/xsd/1.0 palinagent/daemon/xsd/1.1
```

Then replace the version on the new schema. After you can update all configuration files and also update the
hardcoded files.

```bash
palinagent/daemon/main.py
palinagent/daemon/tests/helpers.py
palinagent/daemon/tests/testXMLConfig.py
```




---
Copyright (C) 2007-2016 ActiveEon
Visit http://proactive.inria.fr/ and http://www.activeeon.com/
Contact: +33 (0)9 88 777 660, contact@activeeon.com 

