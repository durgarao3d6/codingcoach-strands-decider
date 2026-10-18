0. CodingCoach is a Socratic coding tutor. Strands Decider reads every message and picks the right teaching move before the LLM responds — ask, hint, or explain.

1. An AI coding tutor that reads where you are and asks, hints, or explains — never dumps. What it does: Classifies every message before responding: exploring, attempting, stuck, or understanding. Asks questions before explaining — Socratic method, not information dump. Gives the smallest useful hint when you're stuck. Checks your code and names what's right before saying what's wrong.

2. The learner asks about a new concept. Watch the decider classify this as 'exploring' and redirect to a question rather than an explanation. The decider scored , so the verdict was decided, in 7.3 seconds.

3. The learner shows partial understanding. The decider sees 'attempting' and asks the tutor to probe the gap. The decider scored , so the verdict was decided, in 7.0 seconds.

4. The learner shares code with no base case. The decider sees 'attempting' and the tutor checks the answer — naming what is right first. The decider scored , so the verdict was decided, in 7.5 seconds.

5. After repeated attempts, the learner asks directly. The decider sees 'stuck' with needs_direct=yes and the tutor finally explains. The decider scored , so the verdict was decided, in 6.9 seconds.

6. The learner demonstrates understanding. The decider catches it and the tutor offers a challenge. The decider scored , so the verdict was decided, in 6.8 seconds.

7. On 24 labelled decisions, with the decider on the AWS User Group Madurai hosted API, Strands Decider was 88% accurate at a median of 4914 milliseconds, against 88% and 19975 milliseconds for a hosted open LLM asked the same questions.

8. Here is what the numbers actually showed. We ran Strands Decider against a standard language model on the same set of decisions. Both got around the same number right — but the decider did it in about one quarter of the time. That matters because this decision runs on every single message a learner sends. The faster it is, the less the learner has to wait before the tutor responds. And at a fraction of the cost, it is practical to run it in production, not just in a demo. The bigger point is this: a language model is a powerful thing, but it does not always need to write a paragraph to answer a question. Sometimes all you need is a label and a confidence score. When that is enough, use something built for exactly that job.