# TODO

# check

- [ ] tilting simulation seems strong, transmittance seems wrong

## Issue

- [ ] infinit loop lost signal
- [ ] resolution which worked breaks now the init process, also infinit loop
- [ ] plot (FOM) does not change when offset changes
- [ ] rho line does not change if offset is changed
- [ ] resolution

- [x] slow save menu
  - sloved by pausing worker
  - for big videos also if plot and segment overlay is disabled
  - if number of points in line > 3 for small video
  - gets better if qtimer is less frequent
  - @timing for worker.next() < 0.03 for 1080p
- [ ] new videos which are working for smaller insert-threshold
- [ ] plot data is not empty after changing values

## Features

- [ ] tesafilm raus croppen!
- [ ] speichere daten der angeklickten punkte
- [ ] add visual indicator, which menu is active in PLI
- [ ] show coordinate while hovering with mouse
- masking modalities
- [ ] qt drawings as overlayed transparant label?

## RFC

- [ ] tracker uses also only green channel
- [ ] check datatype -> float32 and uint8
- [ ] everything to getter methods?
- [ ] rfc data_classes
- [ ] rfc class names
- [ ] RFC signals. they should be more obvious
- [ ] Readme with gif examples
