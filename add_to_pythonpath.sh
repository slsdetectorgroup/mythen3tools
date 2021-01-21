#echo $#
#if [ $# = 0 ]; then 
#    f=$0
#else
#    f=$1
#fi
#echo $f
if [ "x${BASH_ARGV[0]}" = "x" ]; then
#if [ "x$f" = "x" ]; then
    if [ ! -f this_build_bin_path.sh ]; then
        f=$0
        echo "aaaa"
    #thispath=$(dirname ${BASH_ARGV[0]})  
    thispath=$(dirname $f) 
    p=$(cd ${thispath};pwd); 
    THIS_PATH="$p"
   #     echo "ERROR: must cd where/this/package/is before calling this_path.sh"
#       echo "Try sourcing it"                                 
    else
        echo "bbb"
        THIS_PATH="$PWD"; 
    fi                        
else        
    thispath=$(dirname ${BASH_ARGV[0]})
    p=$(cd ${thispath};pwd); 
    THIS_PATH="$p"    
    echo "ccc"
fi   

    echo "this_path="$THIS_PATH  

export PYTHONPATH=$THIS_PATH:$THIS_PATH/patterntools:$THIS_PATH/analysis/:$THIS_PATH/detector:$THIS_PATH/plotting:$THIS_PATH/trimming:$PYTHONPATH
