document.addEventListener('DOMContentLoaded', function() {
    // Reset the form fields if the form was submitted
    if (document.getElementById('text').value || document.getElementById('num_sentences').value) {
        document.getElementById('text').value = '';
        document.getElementById('num_sentences').value = '';
    }
});