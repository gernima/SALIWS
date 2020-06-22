import pickle


def write_class(b, file_name):
    with open(f'levels/{file_name}.txt', 'wb') as out:
        pickle.dump(b, out)


template = [['🌫', '🌫', '🌫', '🌫', '🌫', '🚪', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
            ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫']
            ]
# road= 🌫
level1 = [['🌲', '🚪', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌫', '🕷', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🕷', '🌲', '🌫', '🌫', '🌫', '🌫', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌫', '🌲', '🌫', '🌲', '🌲', '🌫', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌫', '🌲', '🌫', '🌲', '🌲', '🌫', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🕷:2', '🌫', '🌫', '🌲', '🌲', '🌫', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌫', '🌲', '🌲', '🌲', '🌲', '🌫', '🌫', '🌫', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌫', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌫', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌫', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌫', '🌫', '🌫', '🌲', '🌲'],
          ['🌲', '🌫', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌫', '🌲', '🌲'],
          ['🌲', '🌫', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌫', '🌲', '🌲'],
          ['🌲', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌲', '🌲'],
          ['🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲'],
          ['🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲', '🌲']]
town_Bram_library = [['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '📚', '📚', '📚', '📚', '🌫', '📚', '📚', '📚', '📚', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '📚', '📚', '📚', '📚', '🌫', '📚', '📚', '📚', '📚', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '📚', '📚', '📚', '🌺', '🌫', '🌺', '📚', '📚', '📚', '🌫'],
                     ['🌫', '📚', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '📚', '🌫'],
                     ['🌫', '📚', '🌫', '🌸', '🌫', '🌫', '👩🏼‍🏫', '🌸', '🌫', '📚', '🌫'],
                     ['🌫', '🌺', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌺', '🌫'],
                     ['🌫', '🌸', '🌺', '🌫', '🌫', '🌫', '🌫', '🌫', '🌺', '🌸', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🚪', '🌫', '🌫', '🌫', '🌫', '🌫']]
town_Bram = [['🌫', '🌫', '🌫', '🌫', '🌫', '🚪', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🧵', '🌫', '🌫', '🌫', '📚', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '💰', '💎', '🌕', '🌫', '⚔', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
             ['🌫', '🌫', '🌫', '🌫', '🌫', '🙏', '🌫', '🌫', '🌫', '🌫', '🌫']
             ]
town_Bram_users_shop = [['🌫', '🌫', '🌫', '🌫', '🌫', '🚪', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🌫', '🌫', '🌫', '🌫', '🌫', '👱🏻‍♀', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🚪', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🚪', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                        ]
town_Bram_shop = [['🌫', '🌫', '🌫', '🌫', '🌫', '🚪', '🌫', '🌫', '🌫', '🌫', '🌫'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🙋🏻', '🌫', '🌫', '🌫', '🌫', '🌫'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🚪'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🚪'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                  ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫']
                  ]
town_Bram_auction = [['🌫', '🌫', '🌫', '🌫', '🌫', '🚪', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🙋🏼', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🚪', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🚪'],
                     ['🚪', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🚪'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                     ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫']
                     ]
town_Bram_sewing = [['🌫', '🌫', '🌫', '🌫', '🌫', '🚪', '🌫', '🌫', '🌫', '🌫', '🌫'],
                    ['🌫', '👔', '👔', '👔', '🌫', '🌫', '🌫', '👗', '👗', '👗', '🌫'],
                    ['🌫', '🌫', '👨🏻‍⚖', '👔', '🌫', '🌫', '🌫', '👗', '👩🏼‍⚖', '🌫', '🌫'],
                    ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                    ['🌫', '🥼', '🌫', '🌫', '🌫', '👰🏼', '🌫', '🌫', '🌫', '🧥', '🌫'],
                    ['🌫', '🥼', '🥼', '🥼', '🌫', '🌫', '🌫', '🧥', '🧥', '🧥', '🌫'],
                    ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                    ['🌫', '🌫', '🌫', '🌫', '🧣', '🌫', '🧣', '🌫', '🌫', '👒', '🌫'],
                    ['🌫', '🌫', '🌫', '🌫', '👘', '👘', '👘', '🌫', '👒', '👒', '🌫'],
                    ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫']
                    ]
town_Bram_arena = [['🌫', '🌫', '🌫', '🌫', '🌫', '🚪', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🧔', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫'],
                   ['🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫', '🌫']
                   ]
write_class(town_Bram, 'town_Bram')
write_class(town_Bram_library, 'town_Bram_library')
write_class(town_Bram_sewing, 'town_Bram_sewing')
write_class(town_Bram_arena, 'town_Bram_arena')
write_class(town_Bram_users_shop, 'town_Bram_users_shop')
write_class(town_Bram_shop, 'town_Bram_shop')
write_class(town_Bram_auction, 'town_Bram_auction')

write_class(level1, 'level1')
