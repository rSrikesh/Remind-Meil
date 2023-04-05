import re
import spacy
import pickle

class Email2Reminder:
    def __init__(self, email_subject, email_body, email_date):
        self.subject = email_subject
        self.body = email_body
        self.date = email_date
        self.nlp = spacy.load('en_core_web_trf')
        self.doc = self.nlp(self.body.lower())
        
        with open("matcher.pkl", "rb") as f:
            self.matcher = pickle.load(f)
        
        self.matches = self.matcher(self.doc)
            
    def extracts(self):
        return {"event" : self.subject,
                
                "tags"  : self.__getMailTags(),
                
                "Date"  : self.__getDate(),
                
                "Time"  : self.__getTime(),
                
                "Links" : self.__getLinks(),
                
                "Venue" : self.__getVenue(),
                
                "Contacts" : self.__getContacts(),
                
                "Organizations": self.__getOrgs(),
                
                "virtual" : self.venue_class == "online"
               
               }
    
    def __getMailTags(self):
        triggers = [str(self.doc[start:end]) for match_id, start, end in self.matches if self.matcher.vocab.strings[match_id] == "trigger"]
        return list(set(triggers))
    
    def __getDate(self):
        time_triggers = []
        
        for match_id, start, end in self.matches:
            if self.matcher.vocab.strings[match_id] == "time trigger":
                time_triggers.append(start)

        if len(time_triggers) == 0:
            return ("", [])

        trigger_index = sum(time_triggers)//len(time_triggers)
        
        if len(time_triggers) > 15:
            print("WARNING: TOO MANY TIME TRIGGERS PLEASE REFER TO EMAIL FOR TIME")
        
        
        closest_date = (0, 10000000)
        dates = []

        for ent in self.doc.ents:
            if ent.label_ == "DATE":
                dates.append(ent.text)
                if (ent.start_char - trigger_index) <= closest_date[1]:
                    closest_date = (ent.text, ent.start_char - trigger_index)

        return [closest_date, list(set(dates))]
        
    def __getTime(self):
        times =  []
        for ent in self.doc.ents:
            if ent.label_ in {"TIME"}:
                times.append(ent.text)

        return list(set(times))
    
    def __getLinks(self):
        venue_triggers = list(set([str(self.doc[start:end]) for match_id, start, end in self.matches if self.matcher.vocab.strings[match_id] == "venue trigger"]))
        venue_trig_indexes = []

        for match_id, start, end in self.matches:
            if self.matcher.vocab.strings[match_id] == "venue trigger":
                venue_trig_indexes.append(start)
        
        self.venue_class = "offline"

        for i in venue_triggers:
            if any([j in i for j in ["link", "click here", "online", "virtual", "website"]]):
                self.venue_class = "online"
                break
        
        links = []
        link_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        for match in re.finditer(link_regex, self.body):
            links.append((self.body[match.start(): match.end()], match.start(), match.end()))
            
        venue_index = 0
        if len(venue_trig_indexes) > 0:
            venue_index = sum(venue_trig_indexes)//len(venue_trig_indexes)
        
        best_link = (None, 1000000)

        for link in links:
            if (abs(link[1] - venue_index)) <= best_link[1]:
                best_link = (link[0], abs(link[1] - venue_index))
        
        return [best_link, links]
    
    def __getVenue(self):
        venues = [str(self.doc[start:end]) for match_id, start, end in self.matches if self.matcher.vocab.strings[match_id] == "venue"]

        for ent in self.doc.ents:
            if ent.label_ in {"FAC", "GPE"}:
                venues.append(ent.text)

        return list(set(venues))
    
    def __getContacts(self):
        # Extract phone numbers
        phone_pattern = re.compile(r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        phone_matches = phone_pattern.findall(self.body)
        phone_numbers = list(set([''.join(match) for match in phone_matches]))

        # Extract emails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        email_matches = email_pattern.findall(self.body)
        emails = list(set(email_matches))

        return [phone_numbers, emails]
    
    def __getOrgs(self):
        orgs = [str(self.doc[start:end]) for match_id, start, end in self.matches if self.matcher.vocab.strings[match_id] == "Organization"]

        for ent in self.doc.ents:
            if ent.label_ == "ORG":
                orgs.append(ent.text)

        return list(set(orgs))



# ok = Email2Reminder("Pwc Workshop on 18th March from 2 pm to 4.30 pm", """ We are delighted to inform you that senior leaders from PwC will be visiting Amrita Coimbatore campus on 18th March to conduct a workshop on talent building in Salesforce. This program is open to all pre-final year students from BTech CSE and BTech CSE(AI) (2024 batch)
# The workshop will provide students with an opportunity to learn from industry experts and gain valuable knowledge and skills related to Salesforce and related fields. We believe this workshop will be an excellent platform for students to bridge the gap between industry and academia, and we encourage all students to attend.

# We recommend that students come prepared with questions and take advantage of the opportunity to interact with the team from PwC to gain insights into career opportunities and the latest trends in the field.

# Date: 18th March '23
# Time : 2:00 PM to 3.30 PM
# """, 21)

# print(type(ok.extracts()))