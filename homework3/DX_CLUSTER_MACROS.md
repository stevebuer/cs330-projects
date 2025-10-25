# Useful Macros and Filters for DX Cluster

Based on [AR Cluster 6 documentation](http://www.nc7j.com/arcluster/arusermanual-6)

```
show dx freq>=7000 and freq<=54000
```

```
show dx cont=na
```

## DX Extension Settings

```
set dx extension State Grid
```

## DX Filter Settings

Extensive options are available for DX filters.

```
set dx filter not skimmer and freq>7000 and freq<54000 and (cont=na or SpotterCont=na) and not (Comment=*FT8* or Comment=*FT4*)
```

## Macros

Ten macros are available numbered 0-9.

*show station* to list them.

```
set station macro 1 show wwv
```

## Compound filter can be built using the “AND” and “OR” operators

Examples:

show/dx  band=12 and call=vk0hi
show/dx  band=12 and cty=ja
show/dx  call=dx0dx and (band=12 or band=15)
show/dx  dts>2011-12-17 03:04:55 and dts<2011-12-18 03:04:55
show/dx  call=dx0dx and (comment=*qsl* or comment=*via*)
