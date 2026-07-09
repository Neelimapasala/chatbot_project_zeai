// =========================================
// TRY AGAIN BUTTON
// =========================================

const retryBtn = document.getElementById("retryBtn");

retryBtn.addEventListener("click", function () {

    retryBtn.disabled = true;

    retryBtn.innerHTML = `
        <span class="spinner"></span>
        Retrying...
    `;

    setTimeout(() => {

        retryBtn.innerHTML = `
            <i class="fa-solid fa-rotate-right"></i>
            Try Again
        `;

        retryBtn.disabled = false;

    }, 2000);

});

// =========================================
// CONTACT SUPPORT
// =========================================

const supportBtn = document.querySelector(".support-btn");

const supportCard=document.getElementById("supportCard");

supportBtn.addEventListener("click",()=>{

    supportCard.classList.toggle("show");

});

// =========================================
// FAQ ACCORDION
// =========================================

const faqs = document.querySelectorAll(".faq");

faqs.forEach((faq) => {

    faq.addEventListener("click", function () {

        const alreadyOpen = faq.classList.contains("active");

        // Close all
        faqs.forEach((item) => {

            item.classList.remove("active");

        });

        // Open selected one
        if (!alreadyOpen) {

            faq.classList.add("active");

        }

    });

});

// =========================================
// CARD ANIMATION
// =========================================

window.addEventListener("load", function () {

    const card = document.querySelector(".error-card");

    card.style.opacity = "0";
    card.style.transform = "translateY(30px)";

    setTimeout(() => {

        card.style.transition = ".6s";

        card.style.opacity = "1";
        card.style.transform = "translateY(0)";

    },100);

});

// =========================================
// BUTTON HOVER EFFECT
// =========================================

const buttons = document.querySelectorAll("button");

buttons.forEach((button)=>{

    button.addEventListener("mouseenter",()=>{

        button.style.transition=".3s";

    });

});

// =========================================
// ESC KEY
// =========================================

document.addEventListener("keydown",(event)=>{

    if(event.key==="Escape"){

        const openFaq=document.querySelector(".faq.active");

        if(openFaq){

            openFaq.classList.remove("active");

        }

    }

});