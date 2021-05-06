# TODO

# #Issue

- [x] slow save menu
  - sloved by pausing worker
  - for big videos also if plot and segment overlay is disabled
  - if number of points in line > 3 for small video
  - gets better if qtimer is less frequent
  - @timing for worker.next() < 0.03 for 1080p
- [ ] new videos which are working for smaller insert-threshold
- [ ] multiple xy clicks
- [ ] plot data is not empty after changing values

## Features

- [ ] tilting
  - [ ] as switchable 'pointer' `self.data = self.tilts[mode]`
- [ ] show coordinate while hovering with mouse

## RFC

- [ ] check datatype -> float32 and uint8
- [ ] everything to getter methods?
- [ ] rfc data_classes
- [ ] rfc class names
- [ ] RFC signals. they should be more obvious
- [ ] Readme with gif examples
