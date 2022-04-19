set terminal postscript eps enhanced color solid rounded linewidth 1
set size 0.4,0.4
set xlabel "Amount of Noise"
set ylabel "Recovery"
set output "fig4.eps"
set yrange [0:]
set key samplen .2 spacing .6 font ",8"
set key at 0.275,0.2 horizontal

plot "fig4_data" u 1:8 w lines smooth bezier lc "#a65628" lw 4 t 'NT',\
"fig4_data" u 1:9 w lines smooth bezier lc "#a65628" lw 1 t '',\
"fig4_data" u 1:10 w lines smooth bezier lc "#a65628" lw 1 t '',\
"fig4_data" u 1:11 w lines smooth bezier lc "#ff7f00" lw 4 t 'MST',\
"fig4_data" u 1:12 w lines smooth bezier lc "#ff7f00" lw 1 t '',\
"fig4_data" u 1:13 w lines smooth bezier lc "#ff7f00" lw 1 t '',\
"fig4_data" u 1:14 w lines smooth bezier lc "#984ea3" lw 4 t 'DS',\
"fig4_data" u 1:15 w lines smooth bezier lc "#984ea3" lw 1 t '',\
"fig4_data" u 1:16 w lines smooth bezier lc "#984ea3" lw 1 t '',\
"fig4_data" u 1:17 w lines smooth bezier lc "#4daf4a" lw 4 t 'HSS',\
"fig4_data" u 1:18 w lines smooth bezier lc "#4daf4a" lw 1 t '',\
"fig4_data" u 1:19 w lines smooth bezier lc "#4daf4a" lw 1 t '',\
"fig4_data" u 1:5 w lines smooth bezier lc "#377eb8" lw 4 t 'DF',\
"fig4_data" u 1:6 w lines smooth bezier lc "#377eb8" lw 1 t '',\
"fig4_data" u 1:7 w lines smooth bezier lc "#377eb8" lw 1 t '',\
"fig4_data" u 1:2 w lines smooth bezier lc "#e41a1c" lw 4 t 'NC',\
"fig4_data" u 1:3 w lines smooth bezier lc "#e41a1c" lw 1 t '',\
"fig4_data" u 1:4 w lines smooth bezier lc "#e41a1c" lw 1 t ''
