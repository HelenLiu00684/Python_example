# test.tcl

set scriptDir [file dirname [info script]]
set filePath [file join $scriptDir "tcl_commands.txt"]

#puts "Script directory: $scriptDir"
#puts "Target file path: $filePath"

if {![file exists $filePath]} {
    puts "❌ File not found: $filePath"
    exit 1
}


puts "Open TCL file..."
set fp [open $filePath r]
set content [split [string map {"\r" ""} [read $fp]] "\n"] 
close $fp

#string map {key1 value1 key2 value2 ...} string

#puts "Running TCL script list:\n"
#foreach line $content {
#    puts "Command line: $line"
#}

puts "\nRunning system commands..."
foreach line $content {
    if {$line ne ""} {
        catch {
            #set result [eval exec $line]
            #puts "Command: $line"
            #puts "Result:\n$result\n"
            #set result [exec $line]
            set result [eval exec $line]
            puts "Line: $line \n': $result"

        } errMsg
        # errmsg is a special variable set by catch
        if {[info exists errMsg] && $errMsg ne ""} {
            puts "⚠️ Error executing '$line': $errMsg\n"
        }
    }
}

puts "✅ Tcl finished successfully."





