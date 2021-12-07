var diamInput = document.getElementById("diameter");
var lengthInput = document.getElementById("length");
var threadLInput = document.getElementById("threadL");
var selectedBolt;
var quantity = document.getElementById("quantity");
var price = document.getElementById("price");
var stock = document.getElementById("stock");
var tocart = document.getElementById("tocart");

// adott átmérőjű csavarok kiválasztása a szervertől kapott listából
function getBoltsByDiam(diam, boltsArray) {
    var resultArray = [];
    boltsArray.forEach(element => {
        if (element.nomD == diam) {
            resultArray = resultArray.concat(element);
        }
    });
    return resultArray;
}

// adott átmérőjű és hosszú csavarok kiválasztása
function getBoltsByDiamAndLength(diam, length, boltsArray) {
    var resultArray = [];
    boltsArray.forEach(element => {
        if (element.nomD == diam && element.length == length) {
            resultArray = resultArray.concat(element);
        }
    });
    return resultArray;
}

// a kiválasztott átmérőjű, hosszú és menethosszú csavart megkeressük
function getSelectedbolt(diam, length, thread_length, boltsArray) {
    var i = 0;
    while (i < bolts.length) {
        var element = bolts[i];
        if (element.nomD == diam && element.length == length && element.threadL == thread_length) {
            return element;
        }
        i++;
    }
}

// adott tulajdonság szerint az egyediek megtalálása
function findDistinct(property, boltsArray) {
    var resultArray = [];
    boltsArray.forEach(element => {
        var thisAttribute = element[property];
        if (!resultArray.includes(thisAttribute)) {
            resultArray = resultArray.concat(thisAttribute);
        }
    });
    return resultArray;
}

// a szűrés után nem választható paraméterek kiválaszthatatlanná tétele, válaszhatól választhatóvá tétele
function filterEnabled (property, arrayOfAll, validArray) {
    document.getElementById(property + "Default").selected = true;  // "Válasszon!" kiválasztása
    var options = Array.from(document.getElementById(property).getElementsByTagName("option"));
    options.forEach(element => {
        element.disabled = false;
    });
    var valids = findDistinct(property, validArray);
    arrayOfAll.forEach(element => {
        if (!valids.includes(element)) {
            document.getElementById(property + element).disabled = true;
        }
    });
}

// sütiben tárolt adat beolvasása
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(";");
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        c = c.trim();
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}


lengthInput.disabled = true;
threadLInput.disabled = true;

// műveletek, ha új átmérőt választunk
diamInput.addEventListener("change", () => {
    document.getElementById("diamDefault").disabled = true;
    lengthInput.disabled = false;
    document.getElementById("threadLDefault").selected = true;
    threadLInput.disabled = true;
    filterEnabled("length", boltLengths, getBoltsByDiam(diamInput.value, bolts));
})


// máveletek, ha új hosszt választunk
lengthInput.addEventListener("change", () => {
    document.getElementById("lengthDefault").disabled = true;
    threadLInput.disabled = false;
    filterEnabled("threadL", threadLengths, getBoltsByDiamAndLength(diamInput.value, lengthInput.value, bolts));
})

// műveletek, ha új menethosszt (és ezzel konkrét csavart) választunk
threadLInput.addEventListener("change", () => {
    selectedBolt = getSelectedbolt(diamInput.value, lengthInput.value, threadLInput.value, bolts);
    quantity.disabled = false;
    price.innerHTML = 'Ár: ' + selectedBolt.price + ' Ft';
    price.hidden = false;
    price.style = "border: solid black;";
    stock.hidden = false;
    // megnézzük, van-e raktáron
    if (selectedBolt.qty > 0) {
        stock.innerHTML = "Raktáron";
        stock.style = "color: green;";
        tocart.disabled = false;  // ha van raktáron, kosárba tehető
    } 
    else {
        stock.innerHTML = "Nem elérhető";
        stock.style = "color: red;";
    }
})

// mennyiség változtatására változik az ár
quantity.addEventListener("change", () => {
    price.innerHTML = 'Ár: ' + String(parseInt(quantity.value) * parseInt(selectedBolt.price)) + " Ft";
})

// enter megnyomásakor az oldal hibát dobott, ennek a megszüntetése
quantity.addEventListener("keydown", (e) => {
    if (e.key == "Enter") {
        e.preventDefault();
    }
})

// kosárba helyezés
tocart.addEventListener("click", () => {
    var time = new Date();
    var expiry = new Date(time.getTime() + 1 * 24 * 3600 * 1000); // egy napig tároljuk a sütit
    if (getCookie("cart")) {  // ha már létezik a süti, felülírjuk a meglévők megtartásával
        var cart = JSON.parse(getCookie("cart"));
        if (selectedBolt.id in cart) {  // ha már van benne ebből a termékből, hozzáadjuk
            cart[selectedBolt.id] = cart[selectedBolt.id] + parseInt(quantity.value);
        }
        else {
            cart[selectedBolt.id] = parseInt(quantity.value);
        }
        document.cookie = "cart=" + JSON.stringify(cart) + ";expires=" + expiry.toUTCString() + ";path=/;Secure;";
    }
    else {  // ha még nem létezik a süti, létrehozzuk
        var firstItem = {};
        firstItem[selectedBolt.id] = parseInt(quantity.value);
        document.cookie = "cart=" + JSON.stringify(firstItem) + ";expires=" + expiry.toUTCString() + ";path=/;Secure;";
    }
    window.location = window.location;  // oldal újratöltése
})