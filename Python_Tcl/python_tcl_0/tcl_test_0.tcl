# test.tcl
# Open file in append mode ("a")
# set fp [open "tcl_0_result.txt" "a"]

puts "Running TCL script..."

set result [exec uname -a]
puts "System info 'uname -': $result"

set result [exec cat /proc/stat]
puts "CPU stats 'cat /proc/stat':\n$result"
