# Open the file in read mode
set fp [open "tcl_commands.txt" r]

# Read each line until end of file
while {[gets $fp line] >= 0} {
    puts "Read line: $line"
}

# Close the file after reading
close $fp
