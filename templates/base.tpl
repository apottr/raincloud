<html>
<head>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.13/semantic.min.css" />
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.13/semantic.min.js"></script>
</head>
<body>
<div class="ui grid">
  <div class="two wide column"></div>
  <div class="twelve wide column">
    {% block content %}
    {% endblock %}
  </div>
  <div class="two wide column"></div>
</div>
</body>
</html>
