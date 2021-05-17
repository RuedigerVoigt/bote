# Changelog / History

## Version 1.1.0 stable (2021-05-17)

* Make compatible with the newest version of its sister project `userprovided`. (Older versions still work.)
* The optional parameter `wrap_width` allows you to set after how many characters a line is wrapped. (Defaults to 80).

## Version 1.0.0 stable (2021-01-30)

* Change development status from `beta` to `stable`.
* Check used Python version with the [`compatibility`](https://github.com/RuedigerVoigt/compatibility) package. (A sister-project so development is synchronized.)
* Replaced `unittest` with the `pytest` testing framework and increased test coverage.
* Fixed minor bug: Would not raise an exception if no port was provided for an external server

## Version 0.9.1 beta (2020-10-11)

* Now also test with Python 3.9.

## Version 0.9.0 beta (2020-06-21)

* Initial public release: The `bote` library is the former communication module of its sister-project [exoskeleton](https://github.com/RuedigerVoigt/exoskeleton "GitHub Repository of exoskeleton").
