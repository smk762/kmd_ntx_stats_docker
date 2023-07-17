        <script>
            // init bootstrap tooltips
            $(function () {
                $('[data-toggle="tooltip"]').tooltip({
                    delay: {
                        show: 10,
                        hide: 10
                    }
                })
            })

            // init clipboard buttons
            var btns = document.querySelectorAll('button');
            var clipboard = new ClipboardJS(btns);

            clipboard.on('success', function (e) {
                setTooltip(e.trigger, 'Copied!');
                hideTooltip(e.trigger);
            });

            clipboard.on('error', function (e) {
                console.log(e);
            });

            // init copy btn
            var copy_btn = new ClipboardJS('.copy-btn');

            copy_btn.on('success', function (e) {
                setTooltip(e.trigger, 'Copied!');
                hideTooltip(e.trigger);
            });

            copy_btn.on('error', function (e) {
                console.log(e);
            });

            // init clipboard icon
            var clipboard_icon = new ClipboardJS("#copy_icon");

            clipboard_icon.on('success', function (e) {
                setTooltip(e.trigger, 'Copied!');
                hideTooltip(e.trigger);
            });

            clipboard_icon.on('error', function (e) {
                console.log(e);
            });

            // init clipboard tooltips
            function setTooltip(mdi, message) {
              $(mdi).tooltip('hide')
                .attr('data-original-title', message)
                .tooltip('show');
            }

            function hideTooltip(mdi) {
              setTimeout(function() {
                $(mdi).tooltip('hide');
              }, 1000);
            }

            
            $(document).ready(function() {
                var dt_ids = [];
                $(".dataTable").each(function(){
                    dt_ids.push($(this).attr("id"));
                });
                
                for (i = 0; i < dt_ids.length; i++) {
                    update_dt_search(dt_ids[i]);
                    update_dt_length(dt_ids[i]);
                }
                
                Chart.defaults.global.defaultFontColor = 'white';
                Chart.defaults.global.defaultFontSize = 16;

                // Init tooltips
                $('[data-toggle="tooltip"]').tooltip();
                
                // Init Select2 dropdowns
                $('select').select2();

                
            })

            // Init Datetime picker
            $('.dt_picker').datetimepicker({
                theme:'dark', 
                maxDate:new Date(),
                defaultDate: new Date()
            });

            // Init Date picker
            $('.d_picker').datetimepicker({
                theme:'dark', 
                maxDate:new Date(),
                timepicker: false,
                format:'d.m.Y',
                defaultDate: new Date()
            });
        </script>