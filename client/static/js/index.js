function generateUUID() {
  return 'xxxxxxxxyxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
  });
}

// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    let mainTextBox = document.getElementById("mainTextBox");
    let submitBtn = document.getElementById("submitBtn");
    let output = document.getElementById("output");

   // generate or retrieve the userId
    let userId = localStorage.getItem("userId");
    if (!userId) {
      userId = generateUUID();
      localStorage.setItem("userId", userId); // Save the userId in localStorage
    }


    // Click submit button
    submitBtn.addEventListener("click", function () {
        let userInput = mainTextBox.value;  // Capture user input

        if (userInput) {
          // Clear the previous content
          output.innerHTML = "";
          // Show the loading spinner
          document.querySelector(".loading-spinner").style.display = "block";

          // Send user input to the backend (Flask server)
          fetch("/generate_songs", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ content: userInput }),
          })
            .then((response) => response.json())
            .then((data) => {
              // Hide the loading spinner
              document.querySelector(".loading-spinner").style.display = "none";

              // Display the generated songs from Python
              output.innerText = "Results: " + data.playlist;
            })
            .catch((error) => {
              output.innerText = "Error generating playlist!";
              console.error(error);
            });
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

    // Button to clear conversation history
    clearBtn.addEventListener("click", function () {
        fetch("/reset", {
          method: "POST",
          headers: {
              "Content-Type": "application/json", // Set the correct Content-Type
          },
          body: JSON.stringify({userId}), // Serialize data to JSON
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data.message);
                output.innerText = "Conversation history cleared!";
            })
            .catch((error) => {
                output.innerText = "Error clearing history!";
                console.error(error);
            });
    });

    window.addEventListener("beforeunload", function (event) {
      fetch("/reset", { method: "POST" })
    });


});
