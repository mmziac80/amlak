document.querySelectorAll('.favorite-btn').forEach(button => {
    button.addEventListener('click', function() {
        const propertyId = this.dataset.propertyId;
        const isFavorite = this.dataset.favorite === 'true';
        
        fetch(`/api/properties/${propertyId}/favorite/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const icon = document.getElementById(`favorite-icon-${propertyId}`);
                this.dataset.favorite = !isFavorite;
                icon.style.color = isFavorite ? '' : 'var(--ai-primary)';
            }
        });
    });
});
