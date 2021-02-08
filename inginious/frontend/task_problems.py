# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Displyable problems """

import gettext
import json
from abc import ABCMeta, abstractmethod
from random import Random

from inginious.common.tasks_problems import Problem, CodeProblem, CodeSingleLineProblem, \
    MatchProblem, MultipleChoiceProblem, FileProblem, TestProblem

from inginious.frontend.parsable_text import ParsableText


class DisplayableProblem(Problem, metaclass=ABCMeta):
    """Basic problem """

    @classmethod
    @abstractmethod
    def get_type_name(cls, language):
        pass

    def adapt_input_for_backend(self, input_data):
        """ Adapt the input from web.py for the inginious.backend """
        return input_data

    @classmethod
    def get_renderer(cls, template_helper):
        """ Get the renderer for this class problem """
        return template_helper.get_renderer(False)

    @abstractmethod
    def show_input(self, template_helper, language, seed):
        """ get the html for this problem """
        pass

    @classmethod
    @abstractmethod
    def show_editbox(cls, template_helper, key, language):
        """ get the edit box html for this problem """
        pass

    @classmethod
    @abstractmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return ""


class DisplayableCodeProblem(CodeProblem, DisplayableProblem):
    """ A basic class to display all BasicCodeProblem derivatives """

    def __init__(self, problemid, content, translations, taskfs):
        super(DisplayableCodeProblem, self).__init__(problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(cls, language):
        return _("code")

    def adapt_input_for_backend(self, input_data):
        return input_data

    def show_input(self, template_helper, language, seed):
        """ Show BasicCodeProblem and derivatives """
        header = ParsableText(self.gettext(language,self._header), "rst",
                              translation=self.get_translation_obj(language))
        return template_helper.render("tasks/code.html", inputId=self.get_id(), header=header,
                                      lines=8, maxChars=0, language=self._language, optional=self._optional,
                                      default=self._default)

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableCodeProblem.get_renderer(template_helper).course_admin.subproblems.code(key, True)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return ""


class DisplayableCodeSingleLineProblem(CodeSingleLineProblem, DisplayableProblem):
    """ A displayable single code line problem """

    def __init__(self, problemid, content, translations, taskfs):
        super(DisplayableCodeSingleLineProblem, self).__init__(problemid, content, translations, taskfs)

    def adapt_input_for_backend(self, input_data):
        return input_data

    @classmethod
    def get_type_name(cls, language):
        return _("single-line code")

    def show_input(self, template_helper, language, seed):
        """ Show InputBox """
        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))
        return template_helper.render("tasks/single_line_code.html", inputId=self.get_id(), header=header, type="text",
                                      maxChars=0, optional=self._optional, default=self._default)

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableCodeSingleLineProblem.get_renderer(template_helper).course_admin.subproblems.code(key, False)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return ""


class DisplayableFileProblem(FileProblem, DisplayableProblem):
    """ A displayable code problem """

    def __init__(self, problemid, content, translations, taskfs):
        super(DisplayableFileProblem, self).__init__(problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(cls, language):
        return _("file upload")

    def adapt_input_for_backend(self, input_data):
        try:
            input_data[self.get_id()] = {"filename": input_data[self.get_id()].filename,
                                                  "value": input_data[self.get_id()].value}
        except:
            input_data[self.get_id()] = {}
        return input_data

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableFileProblem.get_renderer(template_helper).course_admin.subproblems.file(key)

    def show_input(self, template_helper, language, seed):
        """ Show FileBox """
        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))
        return template_helper.render("tasks/file.html", inputId=self.get_id(), header=header,
                                      max_size=self._max_size, allowed_exts=self._allowed_exts,
                                      optional=self._optional)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return ""


class DisplayableMultipleChoiceProblem(MultipleChoiceProblem, DisplayableProblem):
    """ A displayable multiple choice problem """

    def __init__(self, problemid, content, translations, taskfs):
        super(DisplayableMultipleChoiceProblem, self).__init__(problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(cls, language):
        return _("multiple choice")

    def show_input(self, template_helper, language, seed):
        """ Show multiple choice problems """
        choices = []
        limit = self._limit
        if limit == 0:
            limit = len(self._choices)  # no limit

        rand = Random("{}#{}#{}".format(self.get_id(), language, seed))

        # Ensure that the choices are random
        # we *do* need to copy the choices here
        random_order_choices = list(self._choices)
        rand.shuffle(random_order_choices)

        if self._multiple:
            # take only the valid choices in the first pass
            for entry in random_order_choices:
                if entry['valid']:
                    choices.append(entry)
                    limit = limit - 1
            # take everything else in a second pass
            for entry in random_order_choices:
                if limit == 0:
                    break
                if not entry['valid']:
                    choices.append(entry)
                    limit = limit - 1
        else:
            # need to have ONE valid entry
            for entry in random_order_choices:
                if not entry['valid'] and limit > 1:
                    choices.append(entry)
                    limit = limit - 1
            for entry in random_order_choices:
                if entry['valid'] and limit > 0:
                    choices.append(entry)
                    limit = limit - 1

        rand.shuffle(choices)

        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))

        return template_helper.render("tasks/multiple_choice.html", pid=self.get_id(), header=header,
                                      checkbox=self._multiple, choices=choices,
                                      func=lambda text: ParsableText(
                                          self.gettext(language, text) if text else "", "rst",
                                          translation=self.get_translation_obj(language))
                                      )

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableMultipleChoiceProblem.get_renderer(template_helper).course_admin.subproblems.multiple_choice(key)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return DisplayableMultipleChoiceProblem.get_renderer(template_helper).course_admin.subproblems.multiple_choice_templates(key)


class DisplayableMatchProblem(MatchProblem, DisplayableProblem):
    """ A displayable match problem """

    def __init__(self, problemid, content, translations, taskfs):
        super(DisplayableMatchProblem, self).__init__(problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(cls, language):
        return _("match")

    def show_input(self, template_helper, language, seed):
        """ Show MatchProblem """
        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))
        return template_helper.render("tasks/match.html", inputId=self.get_id(), header=header)

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableMatchProblem.get_renderer(template_helper).course_admin.subproblems.match(key)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return ""


class DisplayableTestProblem(TestProblem, DisplayableProblem):
    """ A displayable match problem """

    def __init__(self, problemid, content, translations, taskfs):
        super(DisplayableTestProblem, self).__init__(problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(cls, language):
        return _("extra_test")

    def show_input(self, template_helper, language, seed):
        """ Show MatchProblem """
        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))
        return str(DisplayableCodeProblem.get_renderer(template_helper).tasks.extra_test(self.get_id(), header, 8, 0, None, True, None))

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableTestProblem.get_renderer(template_helper).course_admin.subproblems.extra_test(key)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return ""
