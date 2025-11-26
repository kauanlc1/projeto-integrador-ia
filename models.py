exam_data_schema = {
    "type": "object",
    "properties": {
        "Notice": {
            "type": "string",
            "description": "Texto completo do edital"
        },
        "NoticeTitle": {
            "type": "string",
            "description": "Título do edital"
        },
        "NoticeDescription": {
            "type": "string",
            "description": "Descrição breve do edital"
        },
        "JobRoles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Name": {
                        "type": "string",
                        "description": "Nome da vaga"
                    },
                    "Description": {
                        "type": "string",
                        "description": "Breve descrição da vaga"
                    }
                },
                "required": ["Name", "Description"]
            }
        }
    },
    "required": ["Notice", "NoticeTitle", "NoticeDescription", "JobRoles"],
    "additionalProperties": False
}

roadmap_data_schema = {
    "type": "object",
    "properties": {
        "Title": {
            "type": "string",
            "description": "Título do roadmap"
        },
        "Description": {
            "type": "string",
            "description": "Descrição do roadmap"
        },
        "Modules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Title": {
                        "type": "string",
                        "description": "Título do módulo"
                    },
                    "Description": {
                        "type": "string",
                        "description": "Descrição do módulo"
                    },
                    "Order": {
                        "type": "integer",
                        "description": "Ordem do módulo"
                    },
                    "Lessons": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Title": {
                                    "type": "string",
                                    "description": "Título da lição"
                                },
                                "Description": {
                                    "type": "string",
                                    "description": "Conteúdo da lição"
                                },
                                "Order": {
                                    "type": "integer",
                                    "description": "Ordem da lição"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "required": ["Title", "Description", "Modules"],
    "additionalProperties": False
}

questions_schema = {
    "type": "object",
    "properties": {
        "Questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Question": {
                        "type": "string",
                        "description": "Texto da questão"
                    },
                    "OptionA": {
                        "type": "string",
                        "description": "Alternativa A"
                    },
                    "OptionB": {
                        "type": "string",
                        "description": "Alternativa B"
                    },
                    "OptionC": {
                        "type": "string",
                        "description": "Alternativa C"
                    },
                    "OptionD": {
                        "type": "string",
                        "description": "Alternativa D"
                    },
                    "CorrectOption": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D"],
                        "description": "Alternativa correta"
                    },
                    "Order": {
                        "type": "integer",
                        "description": "Ordem da questão"
                    },
                    "Origin": {
                        "type": "string",
                        "enum": ["Assessment", "Module", "Lesson"],
                        "description": "Origem da questão"
                    }
                },
                "required": ["Question", "OptionA", "OptionB", "OptionC", "OptionD", "CorrectOption", "Order", "Origin"],
                "additionalProperties": False
            }
        }
    },
    "required": ["Questions"],
    "additionalProperties": False
}

search_notice_schema = {
    "type": "object",
    "properties": {
        "Notices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Notice": {
                        "type": "string",
                        "description": "Texto completo do edital"
                    },
                    "NoticeTitle": {
                        "type": "string",
                        "description": "Título do edital"
                    },
                    "NoticeDescription": {
                        "type": "string",
                        "description": "Descrição breve do edital"
                    },
                    "JobRoles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Name": {
                                    "type": "string",
                                    "description": "Nome da vaga"
                                },
                                "Description": {
                                    "type": "string",
                                    "description": "Breve descrição da vaga"
                                }
                            },
                            "required": ["Name", "Description"]
                        }
                    }
                },
                "required": ["Notice", "NoticeTitle", "NoticeDescription", "JobRoles"],
                "additionalProperties": False
            }
        }
    },
    "required": ["Notices"],
    "additionalProperties": False
}

schemas_dict = {
    "exam_data_schema": exam_data_schema,
    "roadmap_data_schema": roadmap_data_schema,
    "questions_schema": questions_schema,
    "search_notice_schema": search_notice_schema
}