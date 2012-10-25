(declare-fun ?store (Int Int Int) Int)
(declare-fun ?select (Int Int) Int)
(declare-fun ?PO (Int Int) Int)
(declare-fun ?asChild (Int Int) Int)
(declare-fun ?classDown (Int Int) Int)
(declare-fun ?array (Int) Int)
(declare-fun ?elemtype (Int) Int)
(declare-fun ?is (Int Int) Int)
(declare-fun ?cast (Int Int) Int)
(declare-fun ?Object () Int)
(declare-fun ?null () Int)
(declare-fun ?typeof (Int) Int)
(declare-fun ?asElems (Int) Int)
(declare-fun ?isAllocated (Int Int) Int) 
(declare-fun ?fClosedTime (Int) Int)
(declare-fun ?eClosedTime (Int) Int)
(declare-fun ?max (Int) Int)
(declare-fun ?asLockSet (Int) Int)
(declare-fun ?isNewArray (Int) Int)
(declare-fun ?classLiteral (Int) Int)
(declare-fun ?Class () Int)
(declare-fun ?alloc () Int)
(declare-fun ?arrayType () Int)
(declare-fun ?f (Int) Int)
(declare-fun ?finv (Int) Int)
(declare-fun ?select2 (Int Int Int) Int) 
(declare-fun ?store2 (Int Int Int Int) Int)
(declare-fun ?subtypes (Int Int) Bool)
(declare-fun ?Unbox (Int) Int)
(declare-fun ?UnboxedType (Int) Int)
(declare-fun ?Box (Int Int) Int)
(declare-fun ?System.Object () Int)
(declare-fun ?Smt.true () Int)
(declare-fun ?AsRepField (Int Int) Int)
(declare-fun ?AsPeerField (Int) Int)
(declare-fun ?nullObject () Int)
(declare-fun ?ownerRef_ () Int)
(declare-fun ?ownerFrame_ () Int)
(declare-fun IntsHeap (Int) Int)
(declare-fun ?localinv_ () Int)
(declare-fun ?inv_ () Int)
(declare-fun ?BaseClass_ (Int) Int)
(declare-fun ?typeof_ (Int) Int)
(declare-fun ?PeerGroupPlaceholder_ () Int)
(declare-fun ?ClassRepr (Int) Int)
(declare-fun ?RefArray (Int Int) Int)
(declare-fun Ints_ (Int Int) Int)
(declare-fun ?RefArrayGet (Int Int) Int)
(declare-fun ?elements_ () Int)
(declare-fun ?NonNullRefArray (Int Int) Int)
(declare-fun IntsNotNull_ (Int Int) Int)
(declare-fun ?Rank_ (Int) Int)
(declare-fun ?ValueArray (Int Int) Int)
(declare-fun ?ArrayCategory_ (Int) Int)
(declare-fun ?ArrayCategoryValue_ () Int)
(declare-fun ?ElementType_ (Int) Int)
(declare-fun ?System.Array () Int)
(declare-fun ?allocated_ () Int)
(declare-fun ?StructGet_ (Int Int) Int)
(declare-fun ?AsRangeField (Int Int) Int)
(declare-fun IntsAllocated (Int Int) Int)
(declare-fun IntnRange (Int Int) Bool)
(declare-fun ?isAllocated_ (Int Int) Bool)
(declare-fun ?AsDirectSubClass (Int Int) Int)
(declare-fun ?OneClassDown (Int Int) Int)
(assert (forall ((a Int) (i Int) (e Int))
                (!
                 (= (?select (?store a i e) i) e)
                 :pattern (?store a i e)
                 :weight 0)))
(assert (forall ((a Int) (i Int) (j Int) (e Int))
                (!
                 (or (= i j) (= (?select (?store a i e) j) (?select a j)))
                 :pattern (?select (?store a i e) j)
                 :weight 0)))
(assert (forall ((t0 Int) (t1 Int) (t2 Int))
                (!
                 (or (not (= (?PO t0 t1) 1))
                     (not (= (?PO t1 t2) 1))
                     (= (?PO t0 t2) 1))
                 :pattern ((?PO t0 t1) (?PO t1 t2)))))
(assert (forall ((t0 Int) (t1 Int))
                (!
                 (or (not (= (?PO t0 t1) 1))
                     (not (= (?PO t1 t0) 1))
                     (= t0 t1))
                 :pattern ((?PO t0 t1) (?PO t1 t0)))))
(assert (forall ((t0 Int) (t1 Int) (t2 Int))
                 (!
                  (or (not (= (?PO t0 (?asChild t1 t2)) 1))
                      (= (?classDown t2 t0) (?asChild   t1 t2)))
                  :pattern (?PO t0 (?asChild t1 t2)))))
(assert (forall ((t Int))
                (!
                 (= (?finv (?f t)) t)
                 :pattern (?f t))))
(assert (forall ((t0 Int) (t1 Int) )
                (!
                 (iff (= (?PO t0 (?array t1)) 1)
                      (not (or (not (= t0 (?array (?elemtype t0))))
                               (not (= (?PO (?elemtype t0) t1) 1)))))
                 :pattern (?PO t0 (?array t1)))))
(assert (forall ((x Int) (t Int))
                (!
                 (or (not (= (?is x t) 1))
                     (= (?cast x t) x))
                 :pattern (?cast x t))))
(assert (forall ((x Int) (t Int))
                (!
                 (or (not (= (?PO t ?Object) 1))
                     (iff (= (?is x t) 1)
                          (or (= x ?null)
                              (= (?PO (?typeof x) t) 1))))
                 :pattern ((?PO t ?Object) (?is x t)))))
(assert (forall ((e Int) (a Int) (i Int))
                (!
                 (= (?is (?select (?select (?asElems e) a) i)
                         (?elemtype (?typeof a))) 1)
                 :pattern (?select (?select (?asElems e) a) i))))
(assert (forall ((x Int) (f Int) (a0 Int))
                (!
                 (or (<= (+ a0 (* -1 (?fClosedTime f))) 0)
                     (not (= (?isAllocated x a0) 1))
                     (= (?isAllocated (?select f x) a0) 1))
                 :pattern (?isAllocated (?select f x) a0))))
(assert (forall ((a Int) (e Int) (i Int) (a0 Int))
                (!
                 (or (<= (+ a0 (* -1 (?eClosedTime e))) 0)
                     (not (= (?isAllocated a a0) 1))
                     (= (?isAllocated (?select (?select e a) i) a0) 1))
                 :pattern (?isAllocated (?select (?select e a) i) a0))))
(assert (forall ((S Int))
                (!
                 (= (?select (?asLockSet S) (?max (?asLockSet S))) 1)
                 :pattern (?select (?asLockSet S) (?max (?asLockSet S))))))
(assert (forall ((s Int))
                (!
                 (or (not (= 1 (?isNewArray s)))
                     (= (?PO (?typeof s) ?arrayType) 1))
                 :pattern (?isNewArray s))))
(assert (forall ((t Int))
                (!
                 (not (or (= (?classLiteral t) ?null)
                          (not (= (?is (?classLiteral t) ?Class) 1))
                          (not (= (?isAllocated (?classLiteral t) ?alloc) 1))))
                 :pattern (?classLiteral t))))
(assert  (forall ((A Int) (o Int) (f Int) (v Int))
                 (!
                  (= (?select2 (?store2 A o f v) o f) v)
                  :pattern (?store2 A o f v)
                  :weight 0)))
(assert  (forall ((A Int) (o Int) (f Int) (p Int) (g Int) (v Int))
                 (!
                  (or (= o p) (= (?select2 (?store2 A o f v) p g) (?select2 A p g)))
                  :pattern (?select2 (?store2 A o f v) p g)
                  :weight 0)))
(assert  (forall ((A Int) (o Int) (f Int) (p Int) (g Int) (v Int))
                 (!
                  (or (= f g) (= (?select2 (?store2 A o f v) p g) (?select2 A p g)))
                  :pattern (?select2 (?store2 A o f v) p g)
                  :weight 0)))
(assert  (forall ((t Int) (u Int) (v Int))
                 (!
                  (or (not (?subtypes t u))
                      (not (?subtypes u v))
                      (?subtypes t v))
                  :pattern ((?subtypes t u) (?subtypes u v)))))
(assert  (forall ((t Int) (u Int))
                 (!
                  (or (not (?subtypes t u))
                      (not (?subtypes u t))
                      (= t u))
                  :pattern ((?subtypes t u) (?subtypes u t)))))
(assert  (forall ((x Int) (p Int))
                 (!
                  (or (not (?subtypes (?UnboxedType (?Box x p)) ?System.Object))
                      (not (= (?Box x p) p))
                      (= x p))
                  :pattern (?subtypes (?UnboxedType (?Box x p)) ?System.Object))))
(assert  (forall ((h Int) (o Int) (f Int) (T Int))
                 (!
                  (or 
                   (not (= (IntsHeap h) ?Smt.true))
                   (= (?select2 h o (?AsRepField f T)) ?nullObject)
                   (not (or (not (= (?select2 h (?select2 h o (?AsRepField f T)) ?ownerRef_) o))
                            (not (= (?select2 h (?select2 h o (?AsRepField f T)) ?ownerFrame_) T)))))
                  :pattern (?select2 h o (?AsRepField f T)))))
(assert  (forall ((h Int) (o Int) (f Int))
                 (!
                  (or
                   (not (= (IntsHeap h) ?Smt.true))
                   (= (?select2 h o (?AsPeerField f)) ?nullObject)
                   (not (or (not (= (?select2 h (?select2 h o (?AsPeerField f)) ?ownerRef_) (?select2 h o ?ownerRef_)))
                            (not (= (?select2 h (?select2 h o (?AsPeerField f)) ?ownerFrame_) (?select2 h o ?ownerFrame_))))))
                  :pattern (?select2 h o (?AsPeerField f)))))
(assert  (forall ((h Int) (o Int))
                 (!
                  (or 
                   (not (= (IntsHeap h) ?Smt.true))
                   (= (?select2 h o ?ownerFrame_) ?PeerGroupPlaceholder_)
                   (not (?subtypes (?select2 h (?select2 h o ?ownerRef_) ?inv_) (?select2 h o ?ownerFrame_)))
                   (= (?select2 h (?select2 h o ?ownerRef_) ?localinv_) (?BaseClass_ (?select2 h o ?ownerFrame_)))
                   (not (or (not (= (?select2 h o ?inv_) (?typeof_ o)))
                            (not (= (?select2 h o ?localinv_) (?typeof_ o))))))
                  :pattern (?subtypes (?select2 h (?select2 h o ?ownerRef_) ?inv_) (?select2 h o ?ownerFrame_)))))
(assert  (forall ((T Int) (h Int))
                 (!
                  (or (not (= (IntsHeap h) ?Smt.true))
                      (= (?select2 h (?ClassRepr T) ?ownerFrame_) ?PeerGroupPlaceholder_))
                  :pattern (?select2 h (?ClassRepr T) ?ownerFrame_))))
(assert  (forall ((a Int) (T Int) (i Int) (r Int) (heap Int))
                 (!
                  (or (not (= (IntsHeap heap) ?Smt.true))
                      (not (?subtypes (?typeof_ a) (?RefArray T r)))
                      (= (Ints_ (?RefArrayGet (?select2 heap a ?elements_) i) T) ?Smt.true))
                  :pattern ((?subtypes (?typeof_ a) (?RefArray T r)) (?RefArrayGet (?select2 heap a ?elements_) i)))))
(assert  (forall ((a Int) (T Int) (r Int))
                 (!
                  (or (= a ?nullObject) 
                      (not (?subtypes (?typeof_ a) (?RefArray T r)))
                      (= (?Rank_ a) r))
                  :pattern (?subtypes (?typeof_ a) (?RefArray T r)))))
(assert  (forall ((T Int) (ET Int) (r Int))
                 (!
                  (or (not (?subtypes T (?ValueArray ET r)))
                      (= (?ArrayCategory_ T) ?ArrayCategoryValue_))
                  :pattern (?subtypes T (?ValueArray ET r)))))
(assert  (forall ((A Int) (r Int) (T Int))
                 (!
                  (or
                   (not (?subtypes T (?RefArray A r)))
                   (not (or (not (= T (?RefArray (?ElementType_ T) r)))
                            (not (?subtypes (?ElementType_ T) A)))))
                  :pattern (?subtypes T (?RefArray A r)))))
(assert  (forall ((A Int) (r Int) (T Int))
                 (!
                  (or (not (?subtypes T (?ValueArray A r)))
                      (= T (?ValueArray A r)))
                  :pattern (?subtypes T (?ValueArray A r)))))
(assert  (forall ((A Int) (B Int) (C Int))
                 (!
                  (or (not (?subtypes C (?AsDirectSubClass B A)))
                      (= (?OneClassDown C A) B))
                  :pattern (?subtypes C (?AsDirectSubClass B A)))))
(assert  (forall ((o Int) (T Int))
                 (!
                  (iff (= (Ints_ o T) ?Smt.true)
                       (or (= o ?nullObject)
                           (?subtypes (?typeof_ o) T)))
                  :pattern (Ints_ o T))))
(assert  (forall ((o Int) (T Int))
                 (!
                  (iff (= (IntsNotNull_ o T) ?Smt.true)
                       (or (= o ?nullObject)
                           (not (= (Ints_ o T) ?Smt.true))))
                  :pattern (IntsNotNull_ o T))))
(assert  (forall ((h Int) (o Int))
                 (!
                  (or (not (= (IntsHeap h) ?Smt.true))
                      (= o ?nullObject)
                      (not (?subtypes (?typeof_ o) ?System.Array))
                      (not (or (not (= (?select2 h o ?inv_) (?typeof_ o)))
                               (not (= (?select2 h o ?localinv_) (?typeof_ o))))))
                  :pattern ((?subtypes (?typeof_ o) ?System.Array) (?select2 h o ?inv_)))))
(assert  (forall ((h Int) (o Int) (f Int) (T Int))
                 (!
                  (or (not (= (IntsHeap h) ?Smt.true))
                      (IntnRange (?select2 h o (?AsRangeField f T)) T))
                  :pattern (?select2 h o (?AsRangeField f T)))))
(assert  (forall ((h Int) (o Int) (f Int))
                 (!
                  (or
                   (not (= (IntsHeap h) ?Smt.true))
                   (not (= (?select2 h o ?allocated_) ?Smt.true))
                   (= (IntsAllocated h (?select2 h o f)) ?Smt.true))
                  :pattern (IntsAllocated h (?select2 h o f)))))
(assert  (forall ((h Int) (s Int) (f Int))
                 (!
                  (or (not (= (IntsAllocated h s) ?Smt.true))
                      (= (IntsAllocated h (?StructGet_ s f)) ?Smt.true))
                  :pattern (IntsAllocated h (?StructGet_ s f)))))
(assert  (forall ((x Int) (f Int) (a0 Int))
                 (!
                  (or (<= (+ a0 (* -1 (?fClosedTime f))) 0)
                      (not (?isAllocated_ x a0))
                      (?isAllocated_ (?select f x) a0))
                  :pattern (?isAllocated_ (?select f x) a0))))
(assert  (forall ((a Int) (e Int) (i Int) (a0 Int))
                 (!
                  (or (<= (+ a0 (* -1 (?eClosedTime e))) 0)
                      (not (?isAllocated_ a a0))
                      (?isAllocated_ (?select (?select e a) i) a0))
                  :pattern (?isAllocated_ (?select (?select e a) i) a0))))
(assert  (forall ((e Int) (a Int) (i Int))
                 (!
                  (= (?is (?select (?select (?asElems e) a) i)
                          (?elemtype (?typeof a))) ?Smt.true)
                  :pattern (?select (?select (?asElems e) a) i))))
(assert  (forall ((t0 Int) (t1 Int))
                 (!
                  (iff (?subtypes t0 (?array t1))
                       (not (or (not (= t0 (?array (?elemtype t0))))
                                (not (?subtypes (?elemtype t0) t1)))))
                    :pattern (?subtypes t0 (?array t1)))))
(assert  (forall ((t0 Int) (t1 Int) (t2 Int))
                 (!
                  (or (not (?subtypes t0 (?asChild t1 t2)))
                      (= (?classDown t2 t0) (?asChild   t1 t2)))
                  :pattern (?subtypes t0 (?asChild t1 t2)))))
(assert  (forall ((t0 Int) (t1 Int))
                 (!
                  (iff (?subtypes t0 (?array t1))
                       (not (or (not (= t0 (?array (?elemtype t0))))
                                (not (?subtypes (?elemtype t0) t1)))))
                  :pattern (?subtypes t0 (?array t1)))))
(assert  (forall ((x Int) (t Int))
                 (!
                  (or (not (= (?is x t) ?Smt.true))
                      (= (?cast x t) x))
                  :pattern (?cast x t))))
(assert  (forall ((x Int) (t Int))
                 (!
                  (or (not (?subtypes t ?Object))
                      (iff (= (?is x t) ?Smt.true)
                           (or (= x ?null)
                               (?subtypes (?typeof x) t))))
                  :pattern ((?subtypes t ?Object) (?is x t)))))
(assert  (forall ((e Int) (a Int) (i Int))
                 (!
                  (= (?is (?select (?select (?asElems e) a) i)
                          (?elemtype (?typeof a))) 1)
                  :pattern (?select (?select (?asElems e) a) i))))