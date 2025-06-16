// ESLint test dosyası

var unusedVariable = "This variable is never used";
let duplicateVar = 1;
// let duplicateVar = 2; // Duplicate declaration

function testFunction() {
    console.log("Hello World")  // Missing semicolon
    
    if (true) {
        var x = 10
        console.log(x)  // Missing semicolon
    }
    
    // Using == instead of ===
    if (x == 10) {
        console.log("x is 10");
    }
    
    // Unreachable code
    return true;
    console.log("This will never execute");
}

// Function with unused parameter
function unusedParam(param1, param2) {
    return param1;
}

// Using var instead of let/const
for (var i = 0; i < 5; i++) {
    setTimeout(function() {
        console.log(i);  // Classic closure issue
    }, 100);
}

// Missing const for variable that never changes
let constantValue = "I never change";

// Using deprecated features
eval("console.log('Using eval is dangerous')");

// Inconsistent quotes
let str1 = "double quotes";
let str2 = 'single quotes';

// Trailing comma in object (might be flagged depending on config)
let obj = {
    prop1: "value1",
    prop2: "value2",
};

testFunction();