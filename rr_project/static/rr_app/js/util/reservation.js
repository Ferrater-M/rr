let activeForm = null;

function showCancelReason(button) {
  activeForm = button.closest("form");
  document.getElementById("reasonBox").classList.remove("hidden");
  document.getElementById("reasonBox").classList.add("show");
}

function closePopup() {
  document.getElementById("reasonBox").classList.remove("show");
  setTimeout(() => {
    document.getElementById("reasonBox").classList.add("hidden");
  }, 200);
}

function submitCancel() {
  const reason = document.getElementById("cancelReasonInput").value.trim();
  if (!reason) {
    alert("Please enter a reason before submitting.");
    return;
  }

  if (activeForm) {
    activeForm.querySelector(".cancel-reason-input").value = reason;
    activeForm.submit();
  }

  closePopup();
}
