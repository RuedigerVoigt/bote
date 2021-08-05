# Changelog / History

## Version 1.2.1 stable (2021-08-05)

* Marked as compatible with Python 3.10 as tests with release candidate 1 run flawlessly on Linux, MacOS, and Windows.

## Version 1.2.0 stable (2021-07-24)

* Use [custom exceptions](bote/err.py).
* Run tests for Python 3.10 with Beta 4 instead of Beta 3.


## Version 1.1.1 stable (2021-06-24)

* Small code improvements.
* Updated dependencies.
* Impoved code testing:
  * Tests now also run with Python `3.10.0-beta.3` on Ubuntu.
  * Although the code should be platform independent, tests are now also run with MacOS and Windows VMs to be sure.
  * Improved test coverage from 85 to 97%.


## Version 1.1.0 stable (2021-05-17)

* Make compatible with the newest version of its sister project `userprovided`. (Older versions still work.)
* The optional parameter `wrap_width` allows you to set after how many characters a line is wrapped. (Defaults to 80).
* The parameter `recipient` can now be either a string or a dictionary. If it is a string, that address will be used as a recipient as long that is not overwritten. In case you use a dictionary, the behavior is the same if you defined a key named `default`. Defining an additional `admin` key allows you to use the new `send_mail_to_admin` command.

## Version 1.0.0 stable (2021-01-30)

* Change development status from `beta` to `stable`.
* Check used Python version with the [`compatibility`](https://github.com/RuedigerVoigt/compatibility) package. (A sister-project so development is synchronized.)
* Replaced `unittest` with the `pytest` testing framework and increased test coverage.
* Fixed minor bug: Would not raise an exception if no port was provided for an external server

## Version 0.9.1 beta (2020-10-11)

* Now also test with Python 3.9.

## Version 0.9.0 beta (2020-06-21)

* Initial public release: The `bote` library is the former communication module of its sister-project [exoskeleton](https://github.com/RuedigerVoigt/exoskeleton "GitHub Repository of exoskeleton").
