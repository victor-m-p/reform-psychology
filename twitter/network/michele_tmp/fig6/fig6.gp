set terminal postscript eps enhanced color solid rounded linewidth 1
set size 0.4,0.4
set key samplen .1 spacing .4 font ",6"
set key at 2,0.0003
set log xy
set format xy "10^{%L}"
set xlabel "Edge Weight"
set ylabel "Avg Neighbor Edge Weight"

list = system('ls *_weight_neighweight')
do for [file in list] {
   set output file.".eps"
   plot file u ($1+1):2 w lines smooth bezier lw 4 lc "#e41a1c" t '',\
        file u ($1+1):3 w lines smooth bezier lw 1 lc "#e41a1c" t '',\
        file u ($1+1):4 w lines smooth bezier lw 1 lc "#e41a1c" t '',\
}
