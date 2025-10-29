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
            set result [exec $line]
            puts "Line: $line \n': $result"

        } errMsg
        if {[info exists errMsg] && $errMsg ne ""} {
            puts "⚠️ Error executing '$line': $errMsg\n"
        }
    }
}

puts "✅ Tcl finished successfully."





