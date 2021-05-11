# TODO

## Issue

- [ ] infinit loop lost signal
- [ ] resolution which worked breaks now the init process, also infinit loop
- [ ] resolution problem EXIO

- [?] slow save menu
  - sloved by pausing worker
  - for big videos also if plot and segment overlay is disabled
  - if number of points in line > 3 for small video
  - gets better if qtimer is less frequent
  - @timing for worker.next() < 0.03 for 1080p
- [ ] new videos which are working for smaller insert-threshold

## Features

- [ ] add visual indicator, which menu is active in PLI
- [ ] qt drawings as overlayed transparant label?

## RFC

- [ ] check datatype -> float32 and uint8
- [ ] everything to getter methods?
- [ ] rfc data_classes
- [ ] rfc class names
- [ ] RFC signals. they should be more obvious
- [ ] Readme with gif examples
