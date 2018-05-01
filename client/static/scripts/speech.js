function startDictation() {
  if (window.hasOwnProperty('webkitSpeechRecognition')) {
    var recognition = new webkitSpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = function(e) {
      document.getElementById('query').value = e.results[0][0].transcript;
      recognition.stop();
      console.log("Result:  " + e.results[0][0].transcript)
      document.getElementById('query-form').submit();
    };

    recognition.onerror = function(e) {
      recognition.stop();
    }
  }
}