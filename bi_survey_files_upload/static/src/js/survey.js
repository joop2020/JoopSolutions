// bi_survey_customization js
odoo.define('bi_survey_files_upload.survey', function (require) {
    "use strict";

    var form = require('survey.form');
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var SurveyFormWidget = publicWidget.registry.SurveyFormWidget;
    var _t = core._t;


    var SurveyFormWidgetExtend = SurveyFormWidget.include({
        events: _.extend({}, SurveyFormWidget.prototype.events, {
            'change #all_attachment': '_onChangeImage',
        }),

        _onChangeImage: function (ev) {
            var self = ev;

            var attach_count = ev.target.files.length;
            var upload_files = [];

            var ok1 = $(ev.target).attr('data-is_multi_file');
            $(ev.target).parent().find('.image_data_div').empty();

            for (let i = 0; i < attach_count; i++) {
                let file = ev.target.files[i];
                let fr = new FileReader();
                fr.onload = function (file) {
                    let data = fr.result;
                    data = data.split(',')[1];
                    let vals = {
                        name: ev.target.files[i].name,
                        type: ev.target.files[i].type,
                        data: data,
                    };
                    upload_files.push(vals);
                    let img_name = 'img_data_' + i.toString();
                    let view = `<textarea  name="` + img_name + `"   class="` + img_name + `" style="display: none;" >` + JSON.stringify(vals); + `</textarea>`;
                    $(ev.target).parent().find('.image_data_div').append(view);
                };
                fr.readAsDataURL(file);
            }


            if (ok1 == 'True') {
                //$(ev.target).parent().find(".bi_attachment_lbl").hide()
                //$(ev.target).parent().find(".bi_attachment_lbl_multi").hide()
                var attach_count_ok = ev.target.files.length;
                $(ev.target).parent().find('#attach-name-multi').empty();
                for (var i = 0; i < attach_count_ok; i++) {
                    $(ev.target).parent().find('#attach-name-multi').append(ev.target.files[i].name)
                    if (i != (attach_count_ok - 1)) {
                        $(ev.target).parent().find('#attach-name-multi').append(',' + ' ')
                    }
                }
            } else {
                //$(ev.target).parent().find(".bi_attachment_lbl_multi").hide()
                //$(ev.target).parent().find(".bi_attachment_lbl").hide()
                var attach_count_ok = ev.target.files.length;
                $(ev.target).parent().find("#attach-name").empty();
                for (var i = 0; i < attach_count_ok; i++) {
                    $(ev.target).parent().find("#attach-name").append(ev.target.files[i].name)
                    if (i != (attach_count_ok - 1)) {
                        $(ev.target).parent().find("#attach-name").append(',' + ' ')
                    }
                }
            }
            $('.custom_images').val(JSON.stringify(upload_files));
        },

        _prepareSubmitValues: function (formData, params) {
            var self = this;
            formData.forEach(function (value, key) {
                switch (key) {
                    case 'csrf_token':
                    case 'token':
                    case 'page_id':
                    case 'question_id':
                        params[key] = value;
                        break;
                }
            });

            this.$('[data-question-type]').each(function () {
                switch ($(this).data('questionType')) {
                    case 'text_box':
                    case 'char_box':
                    case 'numerical_box':
                        params[this.name] = this.value;
                        break;
                    case 'date':
                        params = self._prepareSubmitDates(params, this.name, this.value, false);
                        break;
                    case 'datetime':
                        params = self._prepareSubmitDates(params, this.name, this.value, true);
                        break;
                    case 'simple_choice_radio':
                    case 'multiple_choice':
                        params = self._prepareSubmitChoices(params, $(this), $(this).data('name'));
                        break;
                    case 'matrix':
                        params = self._prepareSubmitAnswersMatrix(params, $(this));
                        break;
                    case 'upload_file':
                        var attach_count = this.files.length;
                        var upload_files = [];
                        var final = [];
                        for (let i = 0; i < attach_count; i++) {
                            let file = this.files[i];
                            final.push($(this).parent().find('.image_data_div').find('.img_data_' + i).val());
                        }
                        params[this.name] = final;
                        break;
                }
            });
        },

    });
});