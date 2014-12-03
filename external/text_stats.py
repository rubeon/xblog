from html2text import html2text
from textstat import textstat
import logging

logger = logging.getLogger(__name__)

def calculate_readability(post):
    """
    requires an xblog.Post object to work properly (or anything really that 
    implements a "get_full_body" function)
    """
    full_text = post.get_full_body()
    text = html2text(full_text)
    
    res = {}
    
    res['flesch_reading_ease'] = textstat.textstat.flesch_reading_ease(text)
    res['smog'] = textstat.textstat.flesch_reading_ease(text)
    res['coleman_liau'] = textstat.textstat.coleman_liau_index(text)
    res['consensus'] = textstat.textstat.readability_consensus(text)
    
    return res

def main(test_data):
    print(textstat.textstat.flesch_reading_ease(test_data))
    print(textstat.textstat.smog_index(test_data))
    print(textstat.textstat.flesch_kincaid_grade(test_data))
    print(textstat.textstat.coleman_liau_index(test_data))
    print(textstat.textstat.automated_readability_index(test_data))
    print(textstat.textstat.dale_chall_readability_score(test_data))
    print(textstat.textstat.difficult_words(test_data))
    print(textstat.textstat.linsear_write_formula(test_data))
    print(textstat.textstat.gunning_fog(test_data))
    print(textstat.textstat.readability_consensus(test_data))

if __name__ == '__main__':
    test_data = """
    I was sitting in the train this morning, listening to music and reading something on my tablet. This was all according to my morning routine, a quiet and comfortable place, with nothing more serious to worry about than a flat iPad battery.

    About 10 minutes before we reached the final stop, where I would transfer to the train that takes me onward to my own final stop, a pretty girl collapsed.

    She didn't go down like a sack of potatoes, mind you. She was a class act and just sort of gently leaned, and kept on leaning. The lady next to her realized what was happening pretty quickly. She calmly caught her and gently laid her out in the floor, right by my feet. As far as collapses go, it was orderly, graceful even, like a slow-motion stage-faint.

    Once she was safely on the floor, calls went out for anyone who might know first aid. A twenty-something guy in immodest cycling pants confidently stepped forward and started giving orders. He checked her pulse, made sure she was breathing, and went about arranging her body so she wouldn't choke on her tongue, should dire things indeed be happening. But she was breathing fine, and lay there on her side with her hands beneath her face, sleeping peacefully. Right by my feet.

    I wasn't sure what to do. Not in a flustered or chaotic way, more like when you're speaking in public and can't figure out what to do with your hands. It's been well over twenty years since I took first aid, and I don't think you're supposed go straight to leeches and trepanning any more to treat these types of imbalances of the humors. Not knowing what else to do, I just sat there and watched her sleep.

    This felt creepy almost immediately, so I turned back to my reading. I was in the middle of a Tumblr post by Cory Doctorow, something about cyberfreiheit or Disney's Haunted Mansion most likely, and wanted to get to the end of it. This was when my iPad died on me. For just a split-second, sitting there watching the device's spinning wheel of hibernation, I felt like the universe was conspiring to make me miserable, that life could be cruel and unfair. Then I remembered the young lady who was laid out unconscious at my feet, felt guilty, and checked up on her progress.

    She was sitting up but groggy, with people gathered around, asking her if she knew her own name and who was Prime Minister. I realized that if I fainted and people started asking me these kinds of questions, I wouldn't be able to get more than 50% of them correct. There would probably be a lot of sad, slow head-shaking about the young man who was so out of it he doesn't who the Mayor of London was or who chuffed the lorry. Luckily, and to her credit, she was more up to speed on UK current events and was fine, if rattled. We arrived a few minutes late but I made my transfer without any hassles.

    I entered the connecting train and sat down for the final 45 minute train ride into work, wondering what I was going to do with myself without a telescreen to stare at. Right before leaving the station, someone sat down across from me: it was Sleeping Beauty, and though she was ambulant she was definitely looking like something that the cat had dragged in.

    I wasn't sure if her passing out on the morning train was something I should bring up. I thought it could be an ice-breaker, maybe, a way to get a conversation going and pass the time. But then I thought, she might ask what I did to help, seeing as she had been laying on top of my shoes. I was front row center to her collapse, and not only had no impulse to jump in and help, but would probably have done more harm than good had I tried.

    So I put on my headphones and pretended to listen to music, sneaking the occasional glance to see if she was still shaking and pale. And for the life of me I couldn't figure out what to do with my hands.
    """
    main(test_data)
    
else:
    print __name__