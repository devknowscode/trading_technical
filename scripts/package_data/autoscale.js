if (!window.autoscale_range) {
    window.autoscale_range = function (range, min, max, pad = true) {
        if (min != Infinity && max != Infinity) {
            pad = pad ? (max - min) * 0.05 : 0;
            range.start = min - pad
            range.end = max + pad
        }
    }
}

clearTimeout(window.autoscale_timeout);

window.autoscale_timeout = setTimeout(function () {
    "use strict"

    let start_index = cb_obj.start,
        end_index = cb_obj.end;

    let i = Math.max(Math.floor(start_index), 0),
        j = Math.min(Math.ceil(end_index), source.data["High"].length);

    let min = Math.min.apply(null, source.data["Low"].slice(i, j)),
        max = Math.max.apply(null, source.data["High"].slice(i, j));

    autoscale_range(y_range, min, max, true)

    try {
        if (top_range) {
            let max = Math.max.apply(null, top_source.data['High'].slice(i, j)),
                min = Math.min.apply(null, top_source.data['Low'].slice(i, j));
            autoscale_range(top_range, min, max, true);
        }
    } catch (error) {
        console.error('No top range');
    }

    try {
        if (bot_range_1) {
            let max = Math.max.apply(null, bot_source_1.data['High'].slice(i, j)),
                min = Math.min.apply(null, bot_source_1.data['Low'].slice(i, j));
            autoscale_range(bot_range_1, min, max, true);
        }
    } catch (error) {
        console.error('No bottom_1 range');
    }

    try {
        if (bot_range_2) {
            let max = Math.max.apply(null, bot_source_2.data['High'].slice(i, j)),
                min = Math.min.apply(null, bot_source_2.data['Low'].slice(i, j));
            autoscale_range(bot_range_2, min, max, true);
        }
    } catch (error) {
        console.error('No bottom_2 range');
    }

    try {
        if (bot_range_3) {
            let max = Math.max.apply(null, bot_source_3.data['High'].slice(i, j)),
                min = Math.min.apply(null, bot_source_3.data['Low'].slice(i, j));
            autoscale_range(bot_range_3, min, max, true);
        }
    } catch (error) {
        console.error('No bottom_3 range');
    }

    try {
        if (bot_range_4) {
            let max = Math.max.apply(null, bot_source_4.data['High'].slice(i, j)),
                min = Math.min.apply(null, bot_source_4.data['Low'].slice(i, j));
            autoscale_range(bot_range_4, min, max, true);
        }
    } catch (error) {
        console.error('No bottom_4 range');
    }

    try {
        if (bot_range_5) {
            let max = Math.max.apply(null, bot_source_5.data['High'].slice(i, j)),
                min = Math.min.apply(null, bot_source_5.data['Low'].slice(i, j));
            autoscale_range(bot_range_5, min, max, true);
        }
    } catch (error) {
        console.error('No bottom_5 range');
    }
}, 50);
