var form = document.getElementById("paymentForm");
var onlinePayment = document.getElementById("online");
var cardDataFields = document.getElementById("cardData");
var submitButton = document.getElementById("submit");
var cardNumberField = document.getElementById("cardNumber");
var expiryDateField = document.getElementById("expiryDate");
var cvcField = document.getElementById("cvc");

// a bankkártya mezőit csak akkor jelenítse meg, ha az a fizetési mód van kiválasztva
form.addEventListener("click", () => {
    if (onlinePayment.checked) {
        cardDataFields.style = "display: block;";
        submitButton.value = "Fizetés és megrendelés";
        cardNumberField.required = true;
        expiryDateField.required = true;
        cvcField.required = true;
    }
    else {
        cardDataFields.style = "display: none;";
        submitButton.value = "Megrendelés";
        cardNumberField.required = false;
        expiryDateField.required = false;
        cvcField.required = false;
    }
})

// bankkártyaszám formázása gépelés közben
var prevNumUnformatted = "";
cardNumberField.addEventListener("input", () => {
    var numberInput = cardNumberField.value;
    var numUnformatted = numberInput.replace(/ /g, "");

    if (numUnformatted.length == 16) {
        expiryDateField.focus();
    }

    if(numUnformatted.length >= 4 && prevNumUnformatted != numUnformatted){
        var numFormatted = "";
        for (var i = 0; i < Math.ceil(numUnformatted.length/4); i++) {
            numFormatted = numFormatted.concat(numUnformatted.slice(i*4, (i+1)*4), " ");
        }

        if (numFormatted.slice(-1) == " ") {
            numFormatted = numFormatted.slice(0, -1);
        }
        cardNumberField.value = numFormatted;
    }
    prevNumUnformatted = numUnformatted;
})

// dátum formázása gépelés közben
var prevExpUnformatted = "";
expiryDateField.addEventListener("input", () => {
    var expInput = expiryDateField.value;
    var expUnformatted = expInput.replace("/", "");
    
    if (expUnformatted.length == 4) {
        cvcField.focus();
    }

    if (expUnformatted.length >= 2 && prevExpUnformatted != expUnformatted) {
        var expFormatted = expUnformatted.slice(0, 2).concat("/", expUnformatted.slice(2));
        expiryDateField.value = expFormatted;
    }

    prevExpUnformatted = expUnformatted;
})