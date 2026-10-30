/** Independent expectations for module-specific practice exercises. */
export const practice: Record<number, {value:unknown;expected?:unknown;want:boolean}[]> = {
  "0": [
    {
      "value": 24,
      "want": true
    },
    {
      "value": 26,
      "want": true
    },
    {
      "value": 22,
      "want": false
    },
    {
      "value": 24.5,
      "want": false
    }
  ],
  "1": [
    {
      "value": 7,
      "want": true,
      "expected": 7
    },
    {
      "value": "7",
      "want": false,
      "expected": 7
    },
    {
      "value": null,
      "want": false,
      "expected": null
    }
  ],
  "6": [
    {
      "value": "notes__search_notes",
      "want": true
    },
    {
      "value": "search_notes",
      "want": false
    },
    {
      "value": "../__read",
      "want": false
    }
  ],
  "7": [
    {
      "value": 1,
      "want": true
    },
    {
      "value": 20,
      "want": true
    },
    {
      "value": 21,
      "want": false
    },
    {
      "value": "2",
      "want": false
    }
  ],
  "8": [
    {
      "value": 0,
      "want": true,
      "expected": 4
    },
    {
      "value": 4,
      "want": true,
      "expected": 4
    },
    {
      "value": 5,
      "want": false,
      "expected": 4
    },
    {
      "value": 1,
      "want": false,
      "expected": 0
    }
  ],
  "9": [
    {
      "value": "accept",
      "want": true,
      "expected": true
    },
    {
      "value": "accept",
      "want": false,
      "expected": false
    },
    {
      "value": "decline",
      "want": false,
      "expected": true
    },
    {
      "value": "cancel",
      "want": false,
      "expected": true
    }
  ],
  "11": [
    {
      "value": "https://ops/mcp",
      "want": true,
      "expected": "https://ops/mcp"
    },
    {
      "value": "https://ops/mcp/other",
      "want": false,
      "expected": "https://ops/mcp"
    },
    {
      "value": "",
      "want": false,
      "expected": ""
    },
    {
      "value": [
        "https://ops/mcp"
      ],
      "want": false,
      "expected": "https://ops/mcp"
    }
  ],
  "12": [
    {
      "value": "Authorization",
      "want": true
    },
    {
      "value": "assertion",
      "want": true
    },
    {
      "value": "title",
      "want": false
    }
  ],
  "13": [
    {
      "value": "complete",
      "want": true,
      "expected": false
    },
    {
      "value": "complete",
      "want": false,
      "expected": true
    },
    {
      "value": "input_required",
      "want": false,
      "expected": false
    }
  ],
  "14": [
    {
      "value": "Find matching release notes.",
      "want": true
    },
    {
      "value": "  ",
      "want": false
    },
    {
      "value": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "want": false
    }
  ],
  "15": [
    {
      "value": "call-1",
      "want": true,
      "expected": "call-1"
    },
    {
      "value": "call-2",
      "want": false,
      "expected": "call-1"
    },
    {
      "value": "",
      "want": false,
      "expected": ""
    }
  ],
  "16": [
    {
      "value": [
        "workspace:read"
      ],
      "want": false,
      "expected": true
    },
    {
      "value": [
        "workspace:write"
      ],
      "want": true,
      "expected": true
    },
    {
      "value": [
        "workspace:write"
      ],
      "want": false,
      "expected": false
    }
  ],
  "17": [
    {
      "value": "completed",
      "want": true
    },
    {
      "value": "cancelled",
      "want": true
    },
    {
      "value": "failed",
      "want": true
    },
    {
      "value": "input_required",
      "want": false
    },
    {
      "value": "working",
      "want": false
    }
  ],
  "18": [
    {
      "value": "0.3",
      "want": true
    },
    {
      "value": "0.2",
      "want": false
    },
    {
      "value": 0.3,
      "want": false
    }
  ],
  "19": [
    {
      "value": "io.github.anandtopu/lumen-notes",
      "want": true
    },
    {
      "value": "io.github.attacker/lumen-notes",
      "want": false
    },
    {
      "value": "io.github.anandtopu/../secret",
      "want": false
    }
  ],
  "20": [
    {
      "value": "127.0.0.1",
      "want": true
    },
    {
      "value": "localhost",
      "want": true
    },
    {
      "value": "0.0.0.0",
      "want": false
    },
    {
      "value": "localhost.attacker",
      "want": false
    }
  ],
  "21": [
    {
      "value": "search_notes",
      "want": true,
      "expected": 0
    },
    {
      "value": "search_notes",
      "want": false,
      "expected": 1
    },
    {
      "value": "create_note",
      "want": false,
      "expected": 0
    }
  ]
};
