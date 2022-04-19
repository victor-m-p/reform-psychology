tail -n +2 onet_nc.csv | awk 'BEGIN{i=1}{if(!a[$1]){a[$1]=i;i++}if(!a[$2]){a[$2]=i;i++}print a[$1],a[$2]}END{for(x in a) print a[x]"\t"x > "onet_nc.map"}' > onet_nc.txt;
tail -n +2 onet_df.csv | awk 'BEGIN{i=1}{if(!a[$1]){a[$1]=i;i++}if(!a[$2]){a[$2]=i;i++}print a[$1],a[$2]}END{for(x in a) print a[x]"\t"x > "onet_df.map"}' > onet_df.txt;
./infomap onet_nc.txt . -N 100;
./infomap onet_df.txt . -N 100;

