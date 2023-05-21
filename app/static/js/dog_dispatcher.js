
$(document).ready(function () {
  DogApp.socket = new WebSocket('ws://' + document.domain + ':' + location.port + '/ws/42');

  DogApp.emit = function (msg) {
    DogApp.socket.send(JSON.stringify(msg));
  }

  DogApp.socket.onmessage = function (e) {
    var json = JSON.parse(e.data);
    var playerNames = json['playerNames']
    if (playerNames) {
      playerNames.forEach(function (playerName, index) {
        var svg_element = $('text#' + index + 'name')
        svg_element.text(playerName)
      });
    }

    var card = json['card']
    if (card) {
      var idnum = card[0]
      var angle = card[1]
      var x = card[2]
      var y = card[3]

      groupCard = groupBoard.select('g#card' + idnum)

      groupCard.attr({
        transform: 't' + x + ',' + y + 'r' + angle + ' 0 0',
      });
      opacityCard(groupCard);

      // Show this card on the top
      groupBoard.append(groupCard)
    }

    var cards = json['cards']
    if (cards) {
      // Remove existing cards
      $('g.card').remove()

      cards.forEach(function (card_attrs, i) {
        var idnum = card_attrs[0]
        var angle = card_attrs[1]
        var x = card_attrs[2]
        var y = card_attrs[3]
        var filebase = card_attrs[4]
        var descriptionI18N = card_attrs[5]

        id = 'card' + idnum
        var groupCard = groupBoard.g()
        groupCard.node.id = id
        groupCard.attr({
          class: 'card',
        })
        groupCard.drag(card_drag_move, card_drag_start, card_drag_stop);

        groupCard.image(
          "/static/img/cards/" + filebase + ".svg",
          -DogApp.CARD_WIDTH / 2,
          -DogApp.CARD_HEIGHT / 2,
          DogApp.CARD_WIDTH,
          DogApp.CARD_HEIGHT
        );
        var svgMask = groupCard.rect(
          -DogApp.CARD_WIDTH / 2,
          -DogApp.CARD_HEIGHT / 2,
          DogApp.CARD_WIDTH,
          DogApp.CARD_HEIGHT,
          2 // radius
        );
        svgMask.node.id = 'mask'
        opacity = caluclateCardOpacity(x, y)
        svgMask.attr({
          stroke: 'black',
          'stroke-width': 0.1,
          fill: 'gray',
          // opacity: opacity,
        });

        if (opacity < 0.5) {
          // Prevent help text to be displayed if card is hidden
          var title = Snap.parse('<title>' + descriptionI18N + '</title>');
          groupCard.append(title);
        }

        groupCard.animate({ 'transform': 't' + x + ',' + y + 'r' + angle + ',0,0' }, 3000, mina.backout, updateOpacity);
      });
    }

    var moveMarble = function (marble_attrs) {
      var idnum = marble_attrs[0]
      var x = marble_attrs[1]
      var y = marble_attrs[2]

      marble = groupBoard.select('image#marble' + idnum)

      marble.attr({
        x: x,
        y: y,
      });
    }

    var marble = json['marble']
    if (marble) {
      moveMarble(marble)
    }

    var marbles = json['marbles']
    if (marbles) {
      marbles.forEach(function (marble_attrs, i) {
        moveMarble(marble_attrs)
      });
    }
  };
});
