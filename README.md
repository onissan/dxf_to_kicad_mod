# `dxf_to_kicad_mod`
Script that helps with generating kicad footprint from dxf file created from CAD sketch

Create `Kicad` footprint from `DXF` CAD sketch file. It is difficult to create 
intricate `Kicad` footprint. Currently, I am using `Kicad`to design PCBs, 
however this means that I spend plenty of time on footprint design. 
Creating a shape in CAD tools and convert it to the `Kicad` footprint format,
but those DXF imports are not filled. Thus this required some workaround.

A generated footprint from [a dxf file](test_data.dxf):

![footprint sample](sample.png)

The corresponding [`kicad_mod` file](test_data.kicad_mod) which could be viewed
by `Kicad` footprint viewer.

## How it works

It will read the `DXF` file and find lines and arcs (only supporting these two
types so far) which compose a close-loop graphic, it converts arcs to lines and
connected all lines together using `fp_poly` command in `kicad_mod` file. Each
layer is handled separately, the layer name is converted to layer name in
`kicad_mod` file.

## Limitations

* it only support lines and arcs so far, but it could fulfill my requirement so
  far. In the future, I may add more shape support (by converting the shapes to
  lines)
* each line must connect with another line or arc's beginning or end point very
  precisely, as the algorithm searches the points location only. If it is
  overlapped, it will fail to find the connecting point but it will provide some
  hint to tell you where it is lost, you may check the location if it is
  overlapped or not connected well.
* There must not be a line or arc on top another lines in the same layer due to
  the same reason above. Sometimes, people draws two lines on the same location,
  and it very hard to find where. Again the message in command line will provide
  some hints for you.


## how to use
### install python

### install `dxfgrabber`

```
https://github.com/mozman/dxfgrabber.git
```

### clone this `repe`

```
clone https://github.com/pandysong/dxf2kicad_mod.git
cd dxf2kicad_mod
```

### using following command line to generate `kicad_mod`

```
python dxf2kicad_mode "Your-dxf-file-name-here" > "your kicad_mod file.kicad_mod"
```

### Or using `pipenv`

Install `pipenv` is not yet installed:
```
pip install pipenv
```

#### clone this `repo`
```
clone https://github.com/pandysong/dxf2kicad_mod.git
cd dxf2kicad_mod
```

#### using `pipenv` to install dependencies

```
pipenv install
```

#### enable `pipenv`

```
pipenv shell
```

Then use it as normal

```
python dxf2kicad_mod.py test_data.dxf > test_data.kicad_mod
```


