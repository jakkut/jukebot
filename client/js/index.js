// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    let mainTextBox = document.getElementById("mainTextBox");
    let submitBtn = document.getElementById("submitBtn");
    let output = document.getElementById("output");

    // Click submit button
    submitBtn.addEventListener("click", function () {
        let userInput = mainTextBox.value; // Capture text input (use this variable later for whatever)
        if (userInput) {
            output.innerText = "You entered: " + userInput; // Display it on the page
        } else {
            output.innerText = "Please enter a playlist vibe!";
        }
    });

    // Hitting enter key has same effect
    mainTextBox.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();  // Prevent the default new line in text box
            submitBtn.click();  // Trigger the submit button click event
        }
    });

});
