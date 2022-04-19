set terminal postscript eps enhanced color solid rounded linewidth 1
set size 0.4,0.4
set xlabel "Share of Edges in Backbone"
set xrange [*:*] reverse
set log x
unset key

networks = "cs mi tr"

set yrange [-0.1:1.1]
set ylabel "Coverage"
do for [file in networks] {
   set output file."_nodes.eps"
   plot file."_high_salience_skeleton" u 1:2 w lines lc "#4daf4a" lw 4 t '',\
   file."_maximum_spanning_tree" u 1:2 w points lc "#ff7f00" pt 7 t '',\
   file."_naive" u 1:2 w lines lc "#a65628" lw 4 t '',\
   file."_noise_corrected" u 1:2 w lines lc "#e41a1c" lw 4 t '',\
   file."_doubly_stochastic" u 1:2 w points lc "#984ea3" pt 7 t '',\
   file."_disparity_filter" u 1:2 w lines lc "#377eb8" lw 4 t ''
}
